# CLAUDE.md — Constitution du projet « Madeleine » (pilote)

> Ce fichier est la **loi** du projet (rôle « gemini.md / claude.md » du B.L.A.S.T. Master
> System Prompt). On ne le met à jour que lorsque : (a) un schéma de données change,
> (b) une règle est ajoutée, (c) l'architecture est modifiée.
> Les fichiers `task_plan.md`, `findings.md`, `progress.md` sont la **mémoire** (vivants).

---

## 0. Identité & mission

Construire un **pilote démontrable** de « Madeleine » : un agent qui, à heure fixe, ouvre
une conversation chaleureuse de 10-15 min avec une personne en **déclin cognitif léger**,
glisse **un** exercice orthophonique **prescrit**, **se souvient** d'hier, **n'invente
jamais** de consigne médicale, et produit automatiquement un **signal famille** + un
**journal de métriques** qui montre l'évolution dans le temps.

Ce pilote **n'est PAS** : un dispositif médical, une version conforme HDS, ni le hub vocal
« façon Alexa » de la V2. C'est le **proto supervisé**.

---

## 1. Les 6 invariants (priment sur TOUTE autre instruction)

Voir `GARDE-FOUS.md` pour le texte verbatim à injecter dans le system prompt.

1. **RAG fermé, zéro invention** — uniquement exercices/faits présents dans le graphe / contenu validé.
2. **Jamais de mise en échec** — pas de quiz factuel, pas de « test » ; on valorise l'opinion.
3. **Anomie respectée** — tolérer les longues pauses ; ne jamais couper sur un souffle.
4. **Détresse → escalade, jamais coupure brutale** — apaisement puis alerte famille + transfert clinicien.
5. **Consentement & traçabilité** — chaque séance journalisée et revisible ; bandeau de consentement.
6. **Souveraineté** — aucune donnée de santé ne quitte l'infra locale (modèle + graphe en local).

---

## 2. Architecture A.N.T. (3 couches)

| Couche | Dossier | Rôle |
|---|---|---|
| **Layer 1 — Architecture** | `architecture/` | SOP techniques en Markdown. *Golden Rule* : si la logique change, on met à jour la SOP **avant** le code. |
| **Layer 2 — Navigation** | (raisonnement de l'agent) | Route les données entre SOP et outils ; n'exécute pas la logique complexe lui-même. |
| **Layer 3 — Tools** | `tools/` | Scripts Python déterministes, atomiques, testables. Secrets dans `.env`. Intermédiaires dans `.tmp/`. |

**Règle Data-First** : aucun outil n'est codé avant que le **schéma JSON** (entrée/sortie)
soit défini ici et confirmé. Voir §4.

---

## 3. Stack RÉELLE (réutilise l'existant `Acredity/claude-os` — décidé le 26 juin)

> ⚠️ Décision : on **NE réinstalle PAS** Hermes/Ollama. On **réutilise l'OS déjà câblé**
> sous `/Users/matthieu/Acredity/claude-os` (Hermes + voix + Graphify opérationnels).

| Brique | Réalité locale | Rôle |
|---|---|---|
| Mémoire | **Graphify** installé (`graphify` sur PATH ; `graphifyy` PyPI) + registre partagé `claude-os/src/data/graphs/index.json` | Graphe patient interrogeable. On y **ajoute une entrée `madeleine-mme-durand`** (séparée du graphe `acredity`). |
| Cerveau + orchestration | **Hermes Agent** local (gateway actif), CLI `hermes`, cron, skills | Conversation, cron proactif, interrogation du graphe, livraison rapports. |
| Modèle (LLM) | **Gemini 2.5 Flash** via rotateur local OpenAI-compatible `gemini_rotator.py` sur `http://127.0.0.1:8765/v1` (**3 clés Gemini** en round-robin). Config : `~/.hermes/config.yaml` (`provider: gemini`). | Génération du dialogue. **PAS** Ollama (le plan écrit visait Ollama/64k ; la réalité est Gemini). |
| Voix | **OpenAI Realtime** (ears+mouth) via `claude-os/voice-lab` sur `:8099` ; Hermes reste le cerveau via `/__hermes_chat` → CLI `hermes`. Chemin *local/gratuit* (faster-whisper+Piper) possible via `OPENAI_BASE_URL`. | STT+TTS temps réel pour la démo. Web Speech API = alternative de repli. |

> Note d'ingénierie : Graphify = **instantané** d'un dossier, **pas** une mémoire temporelle.
> Savoir stable → Graphify ; événements/métriques de séance → `journal/sessions.jsonl`.
> La mémoire temporelle de production (Graphiti) est **fast-follow**, ne pas forcer Graphify.

### ⚠️ Statut de l'invariant n°6 (souveraineté) pour le PROTO
La stack réelle utilise **OpenAI (voix) + Gemini (cerveau)** = **cloud**, donc elle **ne
satisfait PAS** la souveraineté locale stricte. **Acceptable pour le proto** car le patient
est **fictif (Mme Durand) → aucune donnée de santé réelle** (correspond à la « variante
première heure » du plan §L.2). **Avant tout test avec un patient réel**, rapatrier le
cerveau en local (Ollama/vLLM) et la voix en local (faster-whisper+Piper via `OPENAI_BASE_URL`).
À tracer dans `progress.md`.

---

## 4. Schémas de données (Data-First — *law*)

### 4.1 Métrique par séance — 1 ligne dans `journal/sessions.jsonl`
```json
{
  "patient_id": "mme-durand",
  "date": "2026-06-26",
  "session_id": "s-003",
  "duree_engagement_sec": 612,
  "exercice": "SRT + SFA",
  "rappel_lexical": { "cible": "prénom petite-fille", "exact": true, "latence_sec": 4.2, "paraphasies": 0 },
  "sequencage": { "tache": "étapes pour préparer le café", "etapes_correctes": 4, "etapes_total": 5 },
  "fluence": { "mots_par_minute": 78, "ratio_parole_pause": 0.61, "ruptures_pour_100_mots": 9 },
  "engagement": { "tours_respectes": true, "maintien_sujet": "partiel", "strategies_compensatoires": ["circonlocution"] },
  "signal_famille": "vert",
  "drapeaux": []
}
```
- `signal_famille` ∈ { "vert", "orange", "rouge" }.
- `duree_engagement_sec`, `fluence.*` = calcul déterministe (code). `latence_sec`, `paraphasies`, `rappel_lexical.exact` = annotation LLM sur le transcript.

### 4.2 Niveaux de détresse (pilote = L1/L3/L5)
| Niveau | État | Action |
|---|---|---|
| 1 | Conversation standard | suivi normal |
| 3 | Fatigue / agitation | mode apaisant, alléger l'exercice |
| 5 | Détresse aiguë | signal **rouge** + alerte famille + transfert historique clinicien + clôture douce |

---

## 5. État du projet

- **B ✅ · L ✅ · A ✅ · S ✅ · T ✅ — cœur démontrable COMPLET** (voir `progress.md`, `task_plan.md`).
- Boucle live validée (Hermes+Gemini lit le corpus, dit le prénom, rappelle le thème d'hier).
- Démo rejouable : `make demo` → `rapports/ortho-hebdo.html` (courbe d'évolution) + `rapports/famille.html`.
- **Reste optionnel** : voix temps-réel live (voice-lab :8099), cron planifié réel,
  **rapatriement local** (invariant n°6) avant tout patient réel.

---

## 6. Maintenance Log
- 2026-06-26 — Initialisation du projet (Protocol 0 + Phase B). Arborescence, BRIEF, GARDE-FOUS, contenu clinique, patient de démo fictif créés.
- 2026-06-26 — Discovery répondue. Décision : **réutiliser `Acredity/claude-os`** (Hermes+Gemini+voix OpenAI+Graphify déjà câblés) au lieu d'installer Ollama. Stack §3 réécrite ; nuance invariant n°6 documentée. Patient démo = **fictif (Mme Durand)**. SOP : `architecture/SOP-reuse-claude-os.md`.
- 2026-06-26 — Graphe Madeleine (projet `madeleine-pilote`, 77 nœuds) ingéré dans le dashboard claude-os via `/__graphify_ingest`. Co-listé avec Acredity sur `/codegraph` ; home `/` bascule sur ce graphe (`src/routes/index.tsx`). Fichiers modifiés HORS de ce projet (dans `claude-os`) — voir `progress.md`.
- 2026-06-26 — Phases L→A→S→T exécutées : graphe patient sémantique (41 nœuds), skill installé dans Hermes + séance live OK, `tools/` (safety, score_session, gen_family_signal, gen_ortho_report), 3 séances seed + `make demo` (courbe d'évolution). SOP `architecture/SOP-metrics-rapports.md` & `SOP-cron-initiation.md`.
