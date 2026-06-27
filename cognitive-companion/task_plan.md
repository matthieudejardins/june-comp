# task_plan.md — Pilote « Cognitive Companion » (BLAST)

> Mémoire de planification. Phases, objectifs, checklists. ~3-5 h pour le cœur démontrable.

## Phase B — Brief & Bornes  ✅ (en attente de validation)
**Objectif** : cadrer le périmètre, le critère de succès unique, graver les 6 invariants. *Aucun code.*
- [x] Arborescence projet créée
- [x] `BRIEF.md` (critère de succès unique + tableau de périmètre)
- [x] `GARDE-FOUS.md` (6 invariants, prêts à injecter dans le system prompt)
- [x] `CLAUDE.md` (constitution) + mémoire (`task_plan/findings/progress`)
- [x] Contenu clinique (`exercices.md`, `structure-seance.md`)
- [x] Patient de démo fictif (`patients/mme-durand/*`)
- [ ] **VALIDATION UTILISATEUR + réponses aux questions de Discovery (HALT)**

## Phase L — Lay the rails (RÉVISÉE : réutiliser `Acredity/claude-os`)  ✅
**Objectif** : vérifier le runtime déjà câblé + premier graphe patient interrogeable.
- [x] Gateway Hermes actif (PID 9954) + `hermes` v0.16.0 sur PATH
- [x] Rotateur Gemini OK sur `http://127.0.0.1:8765/v1` (3 clés) — `gemini-2.5-flash` servi
- [x] Voix : réutilise voice-lab `:8099` (OpenAI Realtime) ; Web Speech API en repli (web/index.html)
- [x] Graphe patient SÉMANTIQUE construit : `patients/mme-durand/graphify-out/graph.json`
      (**41 nœuds, 45 liens, 6 communautés** ; routé via le rotateur, `GRAPHIFY_OPENAI_MODEL=gemini-2.5-flash`)
- [x] Interrogation OK : `graphify explain "Camille"` → « Mme Durand --has_granddaughter--> Camille »
- [x] Tracé dans `progress.md` : proto en cloud (invariant n°6 → repatriement avant patient réel)
> Note : le graphe patient est une ressource LOCALE de l'agent (pas une carte dashboard).
> Le graphe PROJET `cognitive-companion` (77 nœuds) reste, lui, indexé dans le dashboard.

## Phase A — Assemble  ◑ (skill + voix + cron écrits ; câblage live à éprouver en S)
**Objectif** : séance vocale complète, 4 phases, personnalisée par le graphe, auto-initiée.
- [x] Skill `companion-session/SKILL.md` complet (rôle, lecture corpus fermé, 4 phases, 6 invariants verbatim, escalade L1/L3/L5, fin de séance → journal)
- [x] Page vocale `web/index.html` (Web Speech API fr-FR, très gros texte/contraste, 1 bouton, endpointing allongé 2.8 s pour l'anomie, repli démo hors-ligne, appel `/__hermes_chat`)
- [x] Cron d'initiation proactive documenté : `architecture/SOP-cron-initiation.md` (9h, un jour sur deux)
- [x] Skill installé dans Hermes (`~/.hermes/skills/companion-session`, enabled) + **séance live OK** :
      `hermes -z … --skills companion-session --yolo` → dit « Geneviève », oriente (vendredi 26 juin),
      rappelle le thème (jardinage/roses, tarte Tatin) — graphe/corpus lus, aucun test, aucune invention.

## Phase S — Simulate & Safeguard  ✅
**Objectif** : éprouver la boucle sur scénarios réalistes, garde-fou détresse actif.
- [x] Garde-fou détresse L1/L3/L5 : `tools/safety.py` (classify_turn + react + false-belief)
- [x] 5 scénarios (`tools/safety.py --selftest`) : Nominal/Anomie/Erreur/Confusion → L1 (zéro fausse escalade) ; L3/L5 OK ; **Confusion → fausse croyance détectée & NON persistée**
- [x] Test « une consigne à la fois » : intégré au skill (séquençage décomposé)

## Phase T — Track & Tell  ✅
**Objectif** : métriques longitudinales → signal famille + rapport ortho avec courbe.
- [x] Schéma métrique §4.1 produit par `tools/score_session.py` → `journal/sessions.jsonl`
- [x] Signal famille `tools/gen_family_signal.py` → `rapports/famille.html` (vert/orange/rouge)
- [x] Rapport ortho `tools/gen_ortho_report.py` → `rapports/ortho-hebdo.html` avec **courbe** (latence 6.8→4.2 s ↓ ; engagement 8.0→10.2 min ↑ ; WPM 64→78 ↑)
- [x] Démo rejouable en une commande : `make demo` (auto-test sécurité + 3 séances + 2 rapports)

---
## Questions de Discovery — RÉPONDUES (26 juin)
1. **Voix** → réutiliser la voix existante de `claude-os` = **OpenAI Realtime** (voice-lab :8099),
   Hermes cerveau. (Web Speech API = repli ; chemin local faster-whisper+Piper = fast-follow.)
2. **Cerveau/modèle** → **Gemini 2.5 Flash** via rotateur local 3 clés (:8765), déjà configuré
   dans `~/.hermes/config.yaml`. (Pas d'Ollama. Repatriement local avant patient réel.)
3. **Patient de démo** → **fictif : Mme Durand** (déjà créé).
4. **Livraison rapports** → via l'OS Hermes existant (connecteurs dispo : WhatsApp activé) OU
   fichiers HTML locaux dans `rapports/` (le plus simple) — à trancher en phase T.
5. **Acronyme BLAST** → conservé (B-L-A-S-T).
