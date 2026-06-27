# findings.md — Recherches, découvertes, contraintes

> Mémoire de recherche. Mise à jour à chaque découverte technique/clinique.

## Contraintes d'ingénierie (issues des deep research)
- **Graphify ≠ mémoire temporelle** : c'est un *instantané* d'un dossier (re-build en watch/git-hook).
  Garder le savoir stable dans Graphify ; les événements/métriques dans `journal/sessions.jsonl`.
  Pour la mémoire temporelle de prod (faits qui se périment) → **Graphiti** (fast-follow).
- **Hermes exige ≥ 64 000 tokens de contexte** ; Ollama est à 4096 par défaut → l'agent déraille
  après 3-4 appels d'outils. FIX : `Modelfile` avec `PARAMETER num_ctx 64000` + `ollama create`.
  **Toujours** vérifier `ollama ps` (colonne CONTEXT = 64000).
- **Endpointing trop agressif** → coupe le patient sur un souffle. Allonger le silence de fin de
  tour (≈2-3 s). Tester explicitement le scénario *Anomie*.
- **Pas de LLM multimodal natif pour analyser la parole** (biais documentés) : séparer transcription
  (LLM) et acoustique (openSMILE, fast-follow).
- **Scope creep clinique** : tout ce qui n'est pas dans la colonne gauche du périmètre est reporté.

## Contraintes cliniques / réglementaires
- **NICE NG97** : proscrire l'« entraînement cognitif » décontextualisé (brain-training) —
  inefficace et anxiogène. Cognitive Companion = stimulation **conversationnelle**.
- **Errorless learning** : en cas d'erreur, indiçage immédiat, jamais de rétroaction négative.
- **HDS obligatoire** en production (DD risque 5) ; écarter les API cloud grand public sans garanties.
- **Matériel** : écarter Echo Show (Fire OS verrouillé) ; viser iPad/Android en mode kiosque (V2).

## DÉCOUVERTE MAJEURE (26 juin) — l'OS est déjà câblé sous `Acredity/claude-os`
Pas besoin d'installer Hermes/Ollama de zéro. Inventaire vérifié sur disque :
- **Hermes** : gateway actif (`~/.hermes/gateway.pid`), CLI `hermes`, skills, cron, mémoire.
- **Modèle** : `~/.hermes/config.yaml` → `provider: gemini`, `default: gemini-2.5-flash`,
  `base_url: http://127.0.0.1:8765/v1`. Le port 8765 = **`gemini_rotator.py`**, shim local
  OpenAI-compatible qui **rotationne 3 clés Gemini** (`~/.hermes/.gemini_rotator_state.json`,
  `rr:1`, 3 clés vues). C'est le « OpenAI + 3 clés Gemini » mentionné par l'utilisateur.
- **Voix** : `claude-os/voice-lab/server.ts` (port **8099**) mint des tokens **OpenAI Realtime**
  (ears+mouth) ; le cerveau reste Hermes via le middleware `/__hermes_chat` (vite.config.ts) →
  spawn du CLI `hermes`. Chemin local/gratuit documenté (`docs/local-voice-setup.md`) :
  pointer `OPENAI_BASE_URL` vers un serveur Realtime local (faster-whisper + Piper).
- **Graphify** : `graphify` sur PATH (`/Library/Frameworks/Python.../bin/graphify`, pkg `graphifyy`).
  Registre partagé `claude-os/src/data/graphs/index.json` (1 entrée `acredity`). Setup idempotent :
  `claude-os/scripts/setup-graphify-brain.sh`. Voir `claude-os/GRAPHIFY.md`.

### Conséquences pour le plan
- Phase L = **vérifier le runtime + ajouter un graphe patient**, pas « installer ».
- L'hypothèse écrite « Ollama + num_ctx=64000 » est **caduque** : la réalité est Gemini-via-rotateur.
  Le fix `num_ctx` Ollama ne s'applique pas. (Garder en tête si on rapatrie en local plus tard.)
- **Invariant n°6 (souveraineté)** : non satisfait par cloud OpenAI+Gemini → **OK pour proto fictif**,
  rapatriement local requis avant patient réel (cf. CLAUDE.md §3).
- Ne PAS mélanger le graphe `acredity` (autre produit) et le graphe Cognitive Companion → entrée registre dédiée.

## (Historique) À vérifier si rapatriement local ultérieur
- Graphify : https://github.com/safishamsi/graphify  ·  Hermes : https://github.com/NousResearch/hermes-agent
- Modèle local selon GPU (hermes4:36b ~21,8 Go / qwen3:14b ~9,3 Go) + `num_ctx=64000`.

## Exercices libres de droits retenus
SRT/EL (récupération espacée sans erreur), SFA (analyse sémantique des traits), RT (réminiscence).
S'inspirer des *principes*, ne pas copier les manuels protégés (CST/UCL, MoCA/MMSE/DO 80).
