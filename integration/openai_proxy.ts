// openai_proxy.ts — proxy local OpenAI-compatible → transfère à api.openai.com avec ta clé.
// Permet à Hermes (adaptateur 'gemini', qui marche) de parler à OpenAI sans toucher l'adaptateur natif.
//   bun run ~/.hermes/openai_proxy.ts        # écoute :8766
import { readFileSync } from "node:fs";

const PORT = Number(process.env.OPENAI_PROXY_PORT || 8766);
const MODEL = process.env.OPENAI_PROXY_MODEL || "gpt-5-chat-latest";
let KEY = process.env.OPENAI_API_KEY || "";
if (!KEY) {
  try {
    for (const l of readFileSync("/Users/matthieu/Acredity/claude-os/.env", "utf8").split("\n")) {
      const m = l.match(/^\s*OPENAI_API_KEY\s*=\s*(.+?)\s*$/);
      if (m) KEY = m[1].replace(/^["']|["']$/g, "");
    }
  } catch {}
}

Bun.serve({
  port: PORT,
  hostname: "127.0.0.1",
  async fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === "/health" || url.pathname === "/v1/models")
      return Response.json({ ok: true, data: [{ id: MODEL, object: "model" }] });
    if (url.pathname.endsWith("/chat/completions") && req.method === "POST") {
      let body: any = {};
      try { body = await req.json(); } catch {}
      body.model = MODEL;                       // force un modèle OpenAI valide
      delete body.safety_settings;              // champs gemini parasites éventuels
      const r = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json" },
        body: JSON.stringify(body),             // garde stream/stream_options tels quels (SSE pass-through)
      });
      console.error(`[proxy] OpenAI ${r.status} (stream=${!!body.stream}, msgs=${(body.messages||[]).length}, tools=${(body.tools||[]).length})`);
      // pipe la réponse OpenAI (SSE si stream:true) directement à Hermes
      return new Response(r.body, { status: r.status, headers: { "Content-Type": r.headers.get("content-type") || "application/json" } });
    }
    return new Response("not found", { status: 404 });
  },
});
console.log(`openai_proxy → http://127.0.0.1:${PORT}  (model ${MODEL}, keyed=${KEY ? "yes" : "NO"})`);
