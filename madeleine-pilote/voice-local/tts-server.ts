// tts-server.ts — Serveur TTS LOCAL (voix macOS naturelle, 0 clé, 0 quota).
// POST /tts { text, voice? } → audio WAV (voix française macOS via `say`).
// Loopback only + CORS pour le dashboard (localhost/127.0.0.1:8081).
//
//   bun run tts-server.ts          # écoute sur :8055
//
import { spawnSync } from "node:child_process";
import { readFileSync, unlinkSync } from "node:fs";

const PORT = Number(process.env.TTS_PORT || 8055);
const DEFAULT_VOICE = process.env.TTS_VOICE || "Audrey";   // voix fr_FR féminine, naturelle
const ALLOWED = new Set(["http://localhost:8081", "http://127.0.0.1:8081"]);

function cors(origin: string) {
  const o = ALLOWED.has(origin) ? origin : "http://localhost:8081";
  return { "Access-Control-Allow-Origin": o, "Vary": "Origin",
           "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" };
}

Bun.serve({
  port: PORT,
  hostname: "127.0.0.1",
  async fetch(req) {
    const url = new URL(req.url);
    const origin = req.headers.get("origin") || "";
    const CORS = cors(origin);
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
    if (url.pathname === "/health") return Response.json({ ok: true, voice: DEFAULT_VOICE }, { headers: CORS });
    if (url.pathname === "/tts" && req.method === "POST") {
      let text = "", voice = DEFAULT_VOICE;
      try { const b = await req.json(); text = String(b.text || "").slice(0, 2000); if (b.voice) voice = String(b.voice); } catch {}
      if (!text.trim()) return new Response(JSON.stringify({ error: "no text" }), { status: 400, headers: { ...CORS, "Content-Type": "application/json" } });
      // garde-fou : voix dans une liste connue (anti-injection argv) + débit posé
      const aiff = `/tmp/mad_tts_${Date.now()}.aiff`;
      const wav = aiff.replace(".aiff", ".wav");
      try {
        const r1 = spawnSync("say", ["-v", voice, "-r", "165", "-o", aiff, text], { timeout: 30000 });
        if (r1.status !== 0) throw new Error("say failed");
        const r2 = spawnSync("afconvert", [aiff, wav, "-d", "LEI16", "-f", "WAVE"], { timeout: 15000 });
        if (r2.status !== 0) throw new Error("afconvert failed");
        const buf = readFileSync(wav);
        try { unlinkSync(aiff); unlinkSync(wav); } catch {}
        return new Response(buf, { headers: { ...CORS, "Content-Type": "audio/wav" } });
      } catch (e: any) {
        try { unlinkSync(aiff); } catch {} try { unlinkSync(wav); } catch {}
        return new Response(JSON.stringify({ error: e?.message || "tts failed" }), { status: 500, headers: { ...CORS, "Content-Type": "application/json" } });
      }
    }
    return new Response("not found", { status: 404, headers: CORS });
  },
});
console.log(`tts-server (voix macOS '${DEFAULT_VOICE}') → http://127.0.0.1:${PORT}`);
