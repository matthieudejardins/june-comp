# SOP — Rapatriement local (souveraineté, invariant n°6)

> Layer 1 (Architect). Objectif : faire tourner **cerveau ET voix en local** avant tout
> **patient réel** (données de santé). Le proto actuel (patient FICTIF) tourne en cloud
> (Gemini + OpenAI Realtime) — **acceptable uniquement pour la démo**.
> Audit non destructif : `bash tools/sovereignty_check.sh`.

## État actuel (26 juin 2026)
- Cerveau : **Gemini 2.5 Flash** via rotateur `:8765` → **cloud**.
- Voix : **OpenAI Realtime** (voice-lab :8099) → **cloud**.
- Ollama : **non installé**. GPU local : non confirmé.
- ⇒ **NON souverain** : interdiction d'enregistrer un patient réel tant que ce SOP n'est pas appliqué.

## A. Cerveau en local (Ollama) — ne PAS casser la config Gemini qui marche
1. Installer Ollama puis le modèle (selon GPU) :
   ```bash
   # macOS : brew install ollama  (ou https://ollama.com/download)
   ollama serve &                       # démon local :11434
   ollama pull qwen2.5:14b              # GPU 12-16 Go  (ou hermes4:36b si ≥24 Go)
   ```
2. **Fix contexte** (Hermes exige ≥ 64k ; Ollama défaut 4096) :
   ```bash
   printf 'FROM qwen2.5:14b\nPARAMETER num_ctx 64000\n' > /tmp/Modelfile.mad
   ollama create madeleine-local -f /tmp/Modelfile.mad
   ollama ps                            # vérifier CONTEXT = 64000
   ```
3. **Bascule réversible** de Hermes (sauvegarder d'abord `~/.hermes/config.yaml`) :
   ```yaml
   model:
     default: madeleine-local
     provider: ollama
     base_url: http://127.0.0.1:11434/v1
   generation: { temperature: 0.3, top_p: 0.9 }
   context:   { max_tokens: 64000 }
   ```
   Retour cloud = restaurer la sauvegarde. (Ou pin par invocation : `hermes -z … -m ollama/madeleine-local`.)

## B. Voix en local (faster-whisper + Piper) — l'OS est déjà prêt
Le voice-lab claude-os route via **un seul env** : `OPENAI_BASE_URL` (cf. `docs/local-voice-setup.md`).
1. Lancer un serveur **OpenAI-Realtime-compatible** local (faster-whisper STT + Piper TTS) sur un port, ex. `8080`.
2. Démarrer le voice-lab pointé dessus :
   ```bash
   cd /Users/matthieu/Acredity/claude-os
   OPENAI_BASE_URL=http://localhost:8080 OPENAI_API_KEY=local bun run voice
   ```
   L'OS n'autorise que `localhost`/`127.0.0.1` (+ api.openai.com) → la clé ne peut pas fuir.
   Alternative pilote 100 % locale & gratuite : `web/index.html` (Web Speech API navigateur).

## C. Vérification
```bash
bash tools/sovereignty_check.sh     # doit afficher : SOUVERAIN — prêt pour un patient RÉEL
```

## D. Reste de conformité avant patient réel (hors scope pilote, cf. plan §5)
Hébergement **HDS**, chiffrement au repos/transit, journal d'audit immuable, **co-signature
du représentant légal**, réversibilité des données. Le rapatriement local (A+B) est nécessaire
mais **pas suffisant** : ne pas enregistrer de patient réel sans ce volet conformité.
