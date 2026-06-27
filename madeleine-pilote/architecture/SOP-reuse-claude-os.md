# SOP — Réutiliser le runtime `Acredity/claude-os` pour le pilote Madeleine

> Layer 1 (Architect). Golden Rule : si la logique change, mettre à jour cette SOP **avant** le code.
> Objectif : ne PAS réinstaller Hermes/Ollama ; brancher Madeleine sur l'OS déjà câblé.

## Composants existants et leur rôle
| Composant | Emplacement | Vérif rapide |
|---|---|---|
| Gateway Hermes | `~/.hermes/` (gateway.pid, config.yaml) | `cat ~/.hermes/gateway.pid` ; processus vivant |
| Cerveau (LLM) | Gemini 2.5 Flash via rotateur | `curl -s http://127.0.0.1:8765/v1/models` (3 clés round-robin) |
| Rotateur Gemini | `~/.hermes/gemini_rotator.py` (+ `.gemini_rotator_state.json`) | état = 3 clés, `rr` incrémente |
| Voix (ears+mouth) | `claude-os/voice-lab/server.ts` port `8099` | `OPENAI_API_KEY=... bun run voice` ; probe `:8099` |
| Bridge voix→cerveau | `claude-os/vite.config.ts` middleware `/__hermes_chat` | spawn du CLI `hermes` |
| Mémoire (graphe) | `graphify` sur PATH + registre `claude-os/src/data/graphs/index.json` | `graphify --help` ; lire `index.json` |

## Procédure Phase L (révisée)
1. **Vérifier le cerveau** : rotateur Gemini répond sur `:8765` ; `~/.hermes/config.yaml`
   pointe bien `provider: gemini`, `base_url: http://127.0.0.1:8765/v1`.
2. **Vérifier la voix** : démarrer voice-lab (`bun run voice` depuis `claude-os`, `OPENAI_API_KEY`
   à clé Realtime), ou décider le chemin local (`OPENAI_BASE_URL=http://localhost:<port>` →
   serveur faster-whisper+Piper). Voir `claude-os/docs/local-voice-setup.md`.
3. **Construire le graphe patient** :
   ```bash
   graphify /Users/matthieu/Madeleine/madeleine-pilote/patients/mme-durand
   # → graph.json / graph.html / GRAPH_REPORT.md
   ```
4. **Enregistrer dans le registre partagé** (entrée DISTINCTE de `acredity`) :
   ajouter à `claude-os/src/data/graphs/index.json` un objet
   `{ "id": "madeleine-mme-durand", "name": "Madeleine — Mme Durand", "path": "…/patients/mme-durand", "graphPath": "…/graph.json", … }`.
5. **Vérifier l'interrogation** : Hermes/Graphify répond cohéremment (ex. voisins de "Camille").

## Garde-fous spécifiques à respecter ici
- **Séparation des produits** : ne jamais fusionner le graphe `acredity` et le graphe Madeleine.
- **Invariant n°6** : stack cloud OK pour proto fictif uniquement ; tracer le repatriement local
  requis avant tout patient réel.
- **Skill `madeleine-session`** : installer comme skill Hermes en phase A ; system prompt = 6
  invariants verbatim (`GARDE-FOUS.md`). Ne pas réutiliser un skill générique de l'OS.
