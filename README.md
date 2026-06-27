# Madeleine — a clinical voice companion on the Claude Code OS

**June Comp entry.** A new feature for the Claude Code Agentic OS: it turns the OS into
**Madeleine**, a voice that runs a daily speech-therapy session for someone with early
cognitive decline. The patient's whole memory is a graphify knowledge graph, Hermes is the
brain, and OpenAI Realtime is the voice.

The patient here (Geneviève Durand, 78) is **fictional**.

## Why this is different
Most OS features are developer tools. This one is a real, high-stakes use case (speech
therapy for cognitive decline), built entirely from the OS's own primitives:

- **The knowledge graph is the patient's memory.** Same graphify engine you'd use on a
  codebase, except the nodes are her family, her garden, her exercises. Hermes queries it;
  the graph lights up as memories connect (roses, tarte Tatin, granddaughter Camille).
- **"Talk to Hermes" becomes a structured therapy session** (voice in, voice out) running
  5 clinical scenarios.
- **It is clinically grounded, not improvised** (see `docs/sources.md`): spaced retrieval,
  semantic cueing, reminiscence, errorless learning, validation therapy, and it refuses what
  the guidelines warn against (decontextualized brain-training).
- **It generalizes.** Same recipe (graph = memory, Hermes = agent) runs on a completely
  different domain (a Brazilian credit project, 1.8M leads). It's an agent factory on the OS.
- **Local / sovereign.** Runs on the machine; patient data stays local.

## The 5 scenarios
Full table in `docs/scenarios.md`. Short version:

| # | Scenario | What Madeleine does | Technique |
|---|---|---|---|
| 1 | Opening | Greets by name, implicit orientation (no test), recalls "last time, your roses" | Ritual + semantic reactivation |
| 2 | Anomia | Graded cues ("starts with C… Ca…") until she says "Camille!" herself | Semantic Feature Analysis + cueing |
| 3 | Error | Never says "no"; gentle redirect, repeat, praise | Errorless Learning |
| 4 | Confusion | Speaks of her late husband as alive → validates, never corrects | Validation therapy |
| 5 | Distress | Slows, soothes; backend raises a green/orange/red family signal | De-escalation + safety layer |

## What's in here
- `madeleine-pilote/` — the build: the `madeleine-session` skill, the patient file
  (`patients/mme-durand`), the clinical content (`contenu-clinique`), the deterministic
  tools (`tools/`: SRT/SFA engine, distress safety classifier, session scoring, family +
  ortho report generators), the browser voice page (`web/index.html`), and SOPs.
- `integration/` — the files that plug into Claude Code OS: the voice-lab server with the
  Madeleine persona, a small OpenAI proxy, and the two graph files.
- `docs/` — the 5 scenarios in detail and the SLP source list.

## Test it
Two ways.

**A. Deterministic core (no keys, instant):**
```bash
cd madeleine-pilote
make test     # safety classifier (5 scenarios) + SRT/SFA engine self-tests
make demo     # replays 3 sessions -> family signal + ortho report with an evolution curve
```

**B. Live voice (needs the Claude Code OS + an OpenAI key):**
1. Drop `integration/voice-lab-server.ts` over `claude-os/voice-lab/server.ts` (it carries
   Madeleine's persona + the patient context).
2. Put `OPENAI_API_KEY=...` in `claude-os/.env`.
3. Run the dashboard and voice-lab, open the Hermes view, hit "Talk to Hermes", and say:
   *"Bonjour Madeleine, on fait notre conversation du matin ?"*
   See `integration/INTEGRATION.md` for the full wiring.

## Demo
60-second Loom: [ADD LINK]

## Note on privacy
The optional personality / linguistic-mirror module (IBM Personality Insights from ~600-1000
words of someone's writing) is **not included** here because the demo used a real person's
data. The clinical voice feature above is fully reproducible with the fictional patient.
