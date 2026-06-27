# progress.md — Journal d'exécution

> Mémoire d'exécution. Ce qui a été fait, erreurs, tests, résultats.

## 2026-06-26 — Protocol 0 + Phase B (Brief & Bornes)
**Fait :**
- Arborescence projet `cognitive-companion/` créée (couches A.N.T. : `architecture/`, `tools/`, `.tmp/`).
- Fichiers mémoire initialisés : `task_plan.md`, `findings.md`, `progress.md`.
- Constitution `CLAUDE.md` créée (identité, 6 invariants, stack, schémas Data-First, état).
- Phase B livrée : `BRIEF.md` (critère de succès + périmètre), `GARDE-FOUS.md` (6 invariants verbatim).
- Contenu clinique : `contenu-clinique/structure-seance.md`, `contenu-clinique/exercices.md`.
- Patient de démo **fictif** : `patients/mme-durand/{bio,famille,faits-a-rappeler,focus-semaine}.md`.
- Squelette scénarios : `tests/scenarios.md` ; placeholders `journal/sessions.jsonl`, `skill/`, `web/`, `architecture/`.

**Erreurs / tests :** aucun (phase sans code).

**État / prochaine étape :**
- **HALT** conforme au B.L.A.S.T. Master System Prompt : pas de code dans `tools/` avant
  réponses Discovery + schéma confirmé + `task_plan.md` approuvé.

## 2026-06-26 (suite) — Discovery répondue + réconciliation de la stack
**Découverte :** l'OS `Acredity/claude-os` est **déjà câblé** (Hermes gateway + voix OpenAI
Realtime `voice-lab:8099` + cerveau **Gemini 2.5 Flash via rotateur 3 clés `:8765`** + Graphify
sur PATH avec registre partagé). Inventaire complet dans `findings.md`.

**Décisions :**
- Phase L **réécrite** : réutiliser claude-os, ne PAS installer Ollama. Ajouter un graphe
  patient `cognitive-companion-mme-durand` au registre (séparé de `acredity`).
- Patient démo = **fictif Mme Durand** (confirmé).
- **Invariant n°6 (souveraineté)** : le proto tournera en **cloud (OpenAI+Gemini)** — accepté
  car patient fictif (aucune PHI réelle) ; **repatriement local obligatoire avant patient réel.**
- SOP de réutilisation rédigée : `architecture/SOP-reuse-claude-os.md`.

**Erreurs / tests :** aucun (toujours phase de cadrage, aucun code écrit).

**Prochaine étape (en attente de feu vert) :** exécuter la Phase L révisée — vérifs runtime
puis `graphify` sur le dossier patient + enregistrement dans le registre.

## 2026-06-26 (suite 2) — Intégration UX : graphe Cognitive Companion dans le dashboard claude-os
**Demande utilisateur :** indexer un graphe Cognitive Companion dans le dashboard, conjointement à Acredity,
sur 2 pages : `/codegraph` (Knowledge Graph, avec visualisation) et `/` (remplacer le graphe actuel).

**Fait :**
- Graphe construit + enregistré via l'endpoint d'ingestion du dashboard (`POST /__graphify_ingest`,
  même chemin que l'UI « Add a project ») : projet **`cognitive-companion`**, nom **« Cognitive Companion »**,
  **77 nœuds · 59 liens · 18 clusters**, god nodes = CLAUDE.md, task_plan, BRIEF, findings, exercices, SOP.
  Fichier : `claude-os/src/data/graphs/cognitive-companion.json` ; entrée ajoutée à `index.json`
  (à côté de `acredity`, couleur `#60a5fa`, description métier).
- **`/codegraph`** : Cognitive Companion apparaît automatiquement dans la galerie avec visualisation 3D
  (la page lit `index.json` / `/__graphify_list`). Item de menu « Knowledge Graph » déjà présent.
- **`/` (home)** : section 2.5 bascule de `acredity.json` → `cognitive-companion.json`
  (`src/routes/index.tsx` : import L31, label « Cognitive Companion », accent `#60a5fa`, légende réécrite).
  Les compteurs nœuds/liens/clusters se recalculent depuis l'import.

**Tests :** `/` et `/codegraph` → HTTP 200 ; `/__graphify_list` renvoie acredity (1350) + cognitive-companion (77).

**Note produits :** Acredity et Cognitive Companion restent **deux graphes séparés** dans le registre
(co-listés, jamais fusionnés). Graphe ingéré = projet `cognitive-companion` complet ; un sous-graphe
patient (`patients/mme-durand`) pour les requêtes de l'agent reste à faire en Phase A/L.

## 2026-06-26 (Phase L + A) — exécution après « Go »
**Phase L (réutilisation runtime) — OK :**
- Runtime vérifié : gateway Hermes PID 9954 vivant ; `hermes` v0.16.0 ; rotateur Gemini sur
  `:8765` sert `gemini-2.5-flash` (+pro/2.0) ; `graphify` sur PATH.
- Graphe patient SÉMANTIQUE construit. `graphify .` échouait (« no LLM API key ») car les .md
  sont des *docs* (extraction sémantique requise). **FIX** : router graphify via le rotateur —
  `OPENAI_API_KEY=<clé .env> OPENAI_BASE_URL=http://127.0.0.1:8765/v1
  GRAPHIFY_OPENAI_MODEL=gemini-2.5-flash GRAPHIFY_ALLOW_LOCAL_PROVIDERS=1 graphify . --no-viz`.
  Résultat : `patients/mme-durand/graphify-out/graph.json` = **41 nœuds, 45 liens, 6 communautés**,
  ~$0.015. Entités correctes (Geneviève, Robert, Hélène, **Camille**, Lucas, Marc, roses, tarte
  Tatin, SRT/EL, SFA, latence d'accès lexical). `graphify explain "Camille"` →
  « Mme Durand --has_granddaughter--> Camille » ✅.

**Phase A (assemble) — écrit :**
- `skill/companion-session/SKILL.md` : skill complet (frontmatter, lecture du corpus fermé,
  4 phases, 6 invariants VERBATIM, errorless, anomie/SFA, gestion confusion=drapeau non persisté,
  escalade L1/L3/L5, fin de séance → schéma JSON → `journal/sessions.jsonl`).
- `web/index.html` : page vocale Web Speech API (fr-FR), très gros texte/contraste, **1 seul**
  bouton, **endpointing allongé 2.8 s** (anomie : on n'est jamais coupé sur un souffle), appel
  `/__hermes_chat` (Hermes=cerveau), **repli démo hors-ligne** qui joue les 4 phases sans réseau.
- `architecture/SOP-cron-initiation.md` : cron 9h un-jour-sur-deux (syntaxe Hermes à confirmer).

**Erreurs / apprentissages (Self-Annealing) :**
- graphify sur un corpus *docs* exige une clé LLM ; le routage via rotateur OpenAI-compatible
  fonctionne (clé `AQ.` acceptée par le rotateur, pas par l'endpoint Gemini natif).
- Build lent (clustering+nommage = plusieurs appels LLM) → lancer en arrière-plan.

**Reste (phase S/T, en attente de feu vert) :** installer le skill dans Hermes & éprouver une
séance live ; garde-fou détresse (`tools/`) ; métriques + rapports + courbe d'évolution.

## 2026-06-26 (Phases S + T + séance live) — exécution après « Go »
**Phase S — garde-fou & scénarios (OK) :**
- `tools/safety.py` : `classify_turn` (L1/L3/L5, marqueurs lexicaux + signaux audio, conservateur),
  `react` (L3=apaisement/orange ; L5=rouge+alerte famille+transfert clinicien+clôture douce),
  `is_false_belief`/`handle_false_belief` (Confusion → drapeau, **non persisté**).
- `python3 tools/safety.py --selftest` → **5/5 PASS** : Nominal/Anomie/Erreur/Confusion=L1
  (zéro fausse escalade), L3/L5 corrects, fausse croyance détectée & isolée.

**Phase T — métriques & rapports (OK) :**
- `tools/score_session.py` : spec → ligne schéma §4.1 → `journal/sessions.jsonl`. Fluence calculée
  (WPM, ratio parole/pause, ruptures/100) à partir de totaux mesurés (`measured`) ; latence/
  paraphasies/maintien = annotations LLM ; `signal_famille` par règle transparente.
- 3 séances simulées (`tests/sessions/s-00{1,2,3}.json`) montrant l'évolution :
  latence **6.8→5.1→4.2 s** (↓), engagement **8.0→9.1→10.2 min** (↑), WPM **64→71→78** (↑),
  ruptures/100 **14→11→9** (↓). Signal : s-001 **orange** (latence≥6), s-002/003 **vert**.
- `tools/gen_family_signal.py` → `rapports/famille.html` ; `tools/gen_ortho_report.py` →
  `rapports/ortho-hebdo.html` avec **2 courbes SVG** inline (latence↓, engagement↑) + tableau.
- `make demo` / `demo.sh` : démo rejouable en une commande (auto-test + scoring + rapports). OK.
- SOP : `architecture/SOP-metrics-rapports.md`.

**Séance LIVE (validation boucle A de bout en bout) :**
- Skill copié dans `~/.hermes/skills/companion-session` (`hermes skills list` = enabled).
- `cd cognitive-companion && hermes -z "<lance Phase 1+2 pour mme-durand>" --skills companion-session --yolo`
  → réponse : « Bonjour **Geneviève**… vendredi 26 juin… les **roses**… hier nous avons parlé de
  votre passion pour le **jardinage**… la **tarte Tatin** du dimanche. » Prénom dit, orientation
  implicite SANS test, thème d'hier rappelé (corpus/graphe lus), aucune consigne inventée. ✅

**Apprentissages (Self-Annealing) :**
- macOS n'a pas `timeout` (utiliser `gtimeout` ou lancer sans).
- WPM calculé sur un extrait de transcript = irréaliste → introduit `measured.{total_words,
  ruptures_count}` (totaux séance) ; le transcript reste un extrait illustratif.

**Statut :** B ✅ · L ✅ · A ✅ (skill+voix+cron+live) · S ✅ · T ✅. Cœur démontrable COMPLET.
Reste optionnel : voix temps-réel (voice-lab live), cron planifié réel, rapatriement local (souveraineté).

## 2026-06-26 (Lot 1 — relecture « Orthophonie et Démence » → renforts cliniques)
Suite à la relecture du doc clinique, 4 renforts livrés (tableau de fiabilité = niveaux de preuve du doc) :
1. **`tools/srt.py`** — automate **Récupération Espacée Sans Erreur (SRT+EL)** : intervalles
   doublants (5s→16m), correction errorless (sans « non »), **retour au dernier palier réussi**,
   **arrêt à 3 échecs consécutifs → diversion** ; + sous-routine **SFA 5 étapes**. `--selftest` ✅.
2. **`web/index.html`** — endpointing **2,8 s → 8 s** (doc : tolérer 8–10 s, anomie) ; débit TTS
   `rate 0.92 → 0.82` (**~120–130 mots/min**, doc CPT). README mis à jour.
3. **skill** — ajout bloc **Adaptation CPT** : **thérapie de validation** (ne jamais corriger une
   confusion de réalité → valider l'émotion ; fausse croyance non persistée), **une consigne ≤10 mots**,
   **pronoms → noms propres**, **questions à choix binaire forcé**, rythme 120–130/silence 8–10 s.
4. **`patients/mme-durand/carnet-de-memoire.md`** — aide mnésique externe (Bourgeois) + **cibles SRT**
   de la semaine ; lu par le skill ; cible d'ancrage « je regarde mon carnet de mémoire ».

Skill resynchronisé dans `~/.hermes/skills/companion-session`. `make test` = safety 5/5 + SRT/SFA ✅.

## 2026-06-26 (Lot 2 + correctif skill + cron + souveraineté)
**Lot 2 — dataset d'exercices :**
- `tools/build_exercise_dataset.py` → `contenu-clinique/exercices_dataset.jsonl` :
  **3 cibles SRT** (dérivées du `carnet-de-memoire.md` du patient) + **10 items SFA** curés sur
  l'univers de la patiente (jardin/cuisine/famille/Loire), chacun avec ses 5 traits sémantiques.
- Honnêteté sources (phd) : **pas de fréquence fabriquée** ; `freq_lexique=null`, difficulté
  qualitative, calibration documentée via **Lexique.org** (freqlemfilms2, CC) en jointure future.
- `tools/srt.py` : ajout `load_dataset()` ; selftest charge le dataset (SRT 3 / SFA 10) ✅.

**Correctif CRITIQUE (signalé par Hermes) — `exercices.md not found` :**
- Cause : le skill utilisait des chemins RELATIFS ; le gateway Hermes ne tourne pas depuis le
  projet → fichiers introuvables. **Fix** : chemins **ABSOLUS** partout dans `SKILL.md`
  (BASE=`/Users/matthieu/Cognitive Companion/cognitive-companion`) + resync Hermes.
- **Vérifié** : `hermes -z … --skills companion-session` lancé **depuis ~** lit bien
  `exercices.md` (« Récupération Espacée… ») et le carnet (« je regarde mon carnet de mémoire »). ✅

**#2 Cron (initiation proactive) — ACTIF :**
- `hermes cron create "0 9 */2 * *" … --name cognitive-companion-mme-durand --skill companion-session
  --deliver local --workdir <projet>` → job `877a5fbcf73f` **active**, prochaine exéc.
  **2026-06-27 09:00**, tous les 2 jours. `hermes cron status` : gateway actif, fire auto. ✅
  (Suppression : `hermes cron rm 877a5fbcf73f`.)

**#3 Souveraineté — kit livré (non destructif) :**
- `tools/sovereignty_check.sh` (audit lecture seule) + `architecture/SOP-souverainete-local.md`
  (rapatriement Ollama num_ctx=64000 + voix locale faster-whisper/Piper via `OPENAI_BASE_URL`).
- Audit actuel : **NON souverain** (cerveau Gemini cloud + voix OpenAI cloud, Ollama absent) →
  OK proto fictif uniquement. Config Gemini live **non modifiée** (démo préservée).

**Voix temps-réel (#1)** : toujours **bloquée** — aucune clé OpenAI Realtime sur disque.
Options : fournir une clé, ou activer la voix locale (SOP §B) / garder Web Speech (`web/index.html`).

`make` : nouveaux targets `dataset`, `sovereignty` (+ `test`, `demo`, `graph`).
