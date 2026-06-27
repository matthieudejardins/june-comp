# Wiring Madeleine into the Claude Code OS

These files plug the feature into an existing Claude Code OS / Hermes install.

## Files
- `voice-lab-server.ts` → copy over `claude-os/voice-lab/server.ts`. It carries the
  Madeleine persona and Geneviève's context directly in the Realtime session `instructions`,
  so the orb voice plays Madeleine (in French), runs the 4-phase session, leads to the
  Camille word-finding exercise, and applies validation therapy. It reads `OPENAI_API_KEY`
  from the env, prefers the server key over any key pasted in the UI, and listens on both
  IPv4 (127.0.0.1) and IPv6 (::1) so the browser reaches it whatever `localhost` resolves to.
- `openai_proxy.ts` → optional. Run with `bun run openai_proxy.ts` (listens on :8766). It is
  an OpenAI-compatible proxy that lets Hermes' `gemini` adapter talk to OpenAI (e.g.
  gpt-5-chat-latest) when you want the brain on OpenAI instead of Gemini. Point Hermes at it:
  in `~/.hermes/config.yaml` set `provider: gemini`, `base_url: http://127.0.0.1:8766/v1`.
- `graphs/madeleine-pilote.json` and `graphs/madeleine-patient.json` → copy into
  `claude-os/src/data/graphs/` and add entries to `index.json` so they show in the Knowledge
  Graph view. `madeleine-patient.json` is the 41-node patient memory the agent reasons over.

## The skill
Install `../madeleine-pilote/skill/madeleine-session` as a Hermes skill (or point the
gateway's skills dir at it). It reads the patient file with absolute paths and holds the
6 invariants verbatim. The voice persona in `voice-lab-server.ts` mirrors the same rules so
the live voice behaves the same way the skill does in text.

## Run
```bash
# from claude-os, Node too old? use bun's runtime:
bun --bun run dev                 # dashboard :8081
bun run voice-lab/server.ts       # voice engine :8099 (reads OPENAI_API_KEY from .env)
```
Open the Hermes view, "Talk to Hermes", say "Bonjour Madeleine, on fait notre conversation
du matin ?". Start a fresh call after any change (the persona loads at call start).

## Not included (privacy)
The dashboard tab `src/routes/madeleine.tsx` and the IBM personality assets are left out of
this repo because they embed a real person's profile. The reproducible feature is the voice
session + graph + skill + deterministic tools, all with the fictional patient.
