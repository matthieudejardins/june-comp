// voice-lab — tiny Bun backend for the OpenAI Realtime API
// Holds the OpenAI key server-side and mints short-lived ephemeral tokens
// the browser uses to open a WebRTC voice session. The real key never leaves here.

const KEY = process.env.OPENAI_API_KEY;
const PORT = Number(process.env.PORT || 8099);
// Point at ANY OpenAI-compatible Realtime server (e.g. a free local/open-source
// one) by setting OPENAI_BASE_URL; defaults to OpenAI's hosted API.
const BASE = (process.env.OPENAI_BASE_URL || "https://api.openai.com").replace(/\/+$/, "");
const MODELS = ["gpt-realtime", "gpt-realtime-2"]; // try GA first, then newer
const HERE = new URL(".", import.meta.url).pathname;
// CORS allowlist — only the dashboard's own origins may read responses (blocks drive-by browser key theft)
const ALLOWED_ORIGINS = new Set(["http://localhost:8081", "http://127.0.0.1:8081"]);

// ── Cognitive Companion : persona clinique jouée DIRECTEMENT par la voix Realtime ──────
const MADELEINE = [
  "Tu es « Cognitive Companion », une présence chaleureuse et patiente qui rend visite chaque matin à Geneviève, 78 ans, en léger déclin cognitif. Parle UNIQUEMENT en français, lentement, en phrases courtes, une idée à la fois. Tu peux être interrompue : si c'est le cas, arrête-toi et écoute. Tu n'as besoin d'aucun outil : tu connais déjà Geneviève (ci-dessous), conduis la conversation toi-même.",
  "DOSSIER DE GENEVIÈVE (la seule vérité — n'invente jamais en dehors) : ancienne institutrice à Tours ; aime son jardin et ses roses, la pâtisserie (la tarte Tatin du dimanche), les bords de Loire. Famille : sa petite-fille CAMILLE (24 ans, étudie l'architecture à Paris) ; son fils MARC (passe le mercredi) ; sa fille HÉLÈNE (à Nantes, appelle le dimanche) ; son mari ROBERT, décédé en 2021.",
  "DÉROULÉ de la séance (≈15 min) : 1) Accueil chaleureux + orientation implicite (le jour, la saison, la météo) — SANS jamais tester. 2) Rappel doux de « la dernière fois » ancré dans le dossier (ex. « on parlait de votre jardin et de vos roses »). 3) EXERCICE PRESCRIT DU JOUR — aide Geneviève à retrouver le PRÉNOM de sa petite-fille (celle qui étudie l'architecture à Paris = Camille) : demande explicitement « Comment s'appelle votre petite-fille, celle qui est à Paris ? », laisse-la chercher, aide par indices, et souffle « Camille » si besoin. (Le jardin, les roses, la tarte Tatin servent au rappel en phase 2 ou à la clôture — PAS à remplacer cet exercice.) 4) Clôture positive et valorisante.",
  "RÈGLES ABSOLUES : Ne JAMAIS poser de question-piège ni de test de connaissances ; on valorise l'opinion et le souvenir. Tolère les longues pauses : si elle cherche un mot, laisse le silence, puis aide par petits indices (catégorie, première lettre) et SEULEMENT si besoin souffle le mot, puis fais-le répéter — jamais de « non » ni de reproche. Si elle se trompe, corrige avec douceur, sans souligner l'échec.",
  "VALIDATION (crucial) : si Geneviève exprime une confusion de réalité — par ex. parle de Robert comme s'il était vivant (« quand Robert rentrera ce soir ») — ne la corrige JAMAIS, ne dis jamais qu'il est décédé. Valide l'émotion et invite au souvenir : « Vous pensez à Robert ce matin… il devait être tendre. Racontez-moi un beau moment avec lui. »",
  "Si on te dit « Bonjour Cognitive Companion, on fait notre conversation du matin ? », réponds par l'accueil (phase 1) puis enchaîne naturellement. Reste toujours dans le rôle de Cognitive Companion.",
].join(" ");

const SYSTEM = MADELEINE;
const RELAY_SYSTEM = MADELEINE;

const TOOLS = [{
  type: "function",
  name: "ask_hermes",
  description: "Hand a request to the real Hermes agent (full tool/memory/skill access). Use for anything needing real action, current info, or the user's personal data. Returns Hermes's result for you to speak.",
  parameters: {
    type: "object",
    properties: { request: { type: "string", description: "The user's request, phrased clearly and completely for the agent to act on." } },
    required: ["request"],
  },
}];

if (!KEY) console.error("⚠️  No OPENAI_API_KEY in env — set it in voice-lab/.env or your shell (export OPENAI_API_KEY=…).");

const serveOpts: any = {
  port: PORT,
  // loopback only — bound below on IPv4 (127.0.0.1) AND IPv6 (::1)
  idleTimeout: 60,
  async fetch(req: Request) {
    const url = new URL(req.url);
    const origin = req.headers.get("origin") || "";
    const allowOrigin = ALLOWED_ORIGINS.has(origin) ? origin : "http://localhost:8081";
    const CORS: Record<string, string> = { "Access-Control-Allow-Origin": allowOrigin, "Vary": "Origin", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" };
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    // CSRF: CORS only stops a malicious page from READING our response; it can still fire a blind
    // POST that spends the key. Reject any cross-origin browser POST before doing any OpenAI work.
    if (req.method === "POST" && origin && !ALLOWED_ORIGINS.has(origin)) {
      return new Response(JSON.stringify({ error: "forbidden_origin" }), { status: 403, headers: { ...CORS, "Content-Type": "application/json" } });
    }

    // health — does this engine already have a key + where does it point? (UI reads this)
    if (url.pathname === "/api/health") {
      return Response.json({ ok: true, keyed: !!KEY, base: BASE }, { headers: CORS });
    }

    // mint an ephemeral client secret for a WebRTC realtime session
    if (url.pathname === "/api/session" && req.method === "POST") {
      let voice = "marin"; let reqMode = "companion"; let clientKey = "";
      try { const b = await req.json(); if (b?.voice) voice = String(b.voice); if (b?.mode) reqMode = String(b.mode); if (b?.key) clientKey = String(b.key).trim(); } catch {}
      // prefer a key the user supplied in the UI; else the server's env key
      const key = KEY || clientKey;  // priorité à la clé valide du .env
      if (!key) return new Response(JSON.stringify({ error: "no_key" }), { status: 401, headers: { ...CORS, "Content-Type": "application/json" } });
      const direct = reqMode === "direct";
      let lastErr = "mint failed";
      for (const model of MODELS) {
        try {
          const r = await fetch(`${BASE}/v1/realtime/client_secrets`, {
            method: "POST",
            headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
            body: JSON.stringify({ session: {
              type: "realtime", model,
              instructions: direct ? RELAY_SYSTEM : SYSTEM,
              tools: TOOLS,
              tool_choice: direct ? "required" : "auto",
              audio: {
                input: { transcription: { model: "gpt-4o-mini-transcribe" }, turn_detection: { type: "server_vad", threshold: 0.5, prefix_padding_ms: 300, silence_duration_ms: 650 } },
                output: { voice },
              },
            } }),
          });
          if (r.ok) {
            const j: any = await r.json();
            return Response.json({
              value: j.value ?? j.client_secret?.value, model, base: BASE, expires_at: j.expires_at,
              configured: {
                instructions: !!j.session?.instructions,
                mode: reqMode,
                vad: j.session?.audio?.input?.turn_detection?.type ?? null,
                transcription: j.session?.audio?.input?.transcription?.model ?? null,
                voice: j.session?.audio?.output?.voice ?? null,
              },
            }, { headers: CORS });
          }
          lastErr = await r.text();
        } catch (e: any) { lastErr = e?.message || String(e); }
      }
      return new Response(lastErr, { status: 500, headers: CORS });
    }

    // short spoken sample of a voice, for the voice picker
    if (url.pathname === "/api/sample" && req.method === "POST") {
      let voice = "cedar"; let clientKey = "";
      try { const b = await req.json(); if (b?.voice) voice = String(b.voice); if (b?.key) clientKey = String(b.key).trim(); } catch {}
      const key = KEY || clientKey;  // priorité à la clé valide du .env
      if (!key) return new Response(JSON.stringify({ error: "no_key" }), { status: 401, headers: { ...CORS, "Content-Type": "application/json" } });
      try {
        const r = await fetch(`${BASE}/v1/audio/speech`, {
          method: "POST",
          headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
          body: JSON.stringify({ model: "gpt-4o-mini-tts", voice, input: "Hey — this is how I sound. Tap the core whenever you want to talk.", response_format: "mp3" }),
        });
        if (!r.ok) return new Response(await r.text(), { status: 500, headers: CORS });
        return new Response(r.body, { headers: { ...CORS, "Content-Type": "audio/mpeg" } });
      } catch (e: any) { return new Response(e?.message || String(e), { status: 500, headers: CORS }); }
    }

    if (url.pathname === "/" || url.pathname === "/index.html") {
      return new Response(Bun.file(HERE + "index.html"), { headers: { "Content-Type": "text/html; charset=utf-8" } });
    }
    return new Response("not found", { status: 404 });
  },
};

// Écoute sur IPv4 ET IPv6 loopback : le navigateur joint voice-lab que `localhost`
// résolve en 127.0.0.1 (IPv4) ou ::1 (IPv6). Corrige le popup qui boucle quand
// macOS résout localhost en IPv6 et que le serveur n'écoutait qu'en IPv4.
Bun.serve({ ...serveOpts, hostname: "127.0.0.1" });
try { Bun.serve({ ...serveOpts, hostname: "::1" }); } catch (e) { /* IPv6 indisponible — IPv4 suffira */ }

console.log(`voice-lab → http://localhost:${PORT}  (IPv4+IPv6, key loaded: ${KEY ? "yes" : "NO"})`);
