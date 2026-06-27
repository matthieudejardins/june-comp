# BRIEF.md — Pilote « Madeleine »

## Critère de succès unique du pilote
> « À J+0 et après 3 séances simulées, je peux montrer à un orthophoniste un rapport qui
> fait apparaître, pour le même patient, une **métrique d'évolution** (ex. latence d'accès
> lexical ou durée d'engagement), et à la famille un **signal vert/orange/rouge** clair —
> sans qu'aucune réponse de l'agent n'ait inventé de consigne médicale ni mis le patient
> en situation d'échec. »

## En une phrase
Un agent qui, à heure fixe, ouvre une conversation chaleureuse de 10-15 min avec une
personne en déclin cognitif léger, glisse 1 exercice orthophonique prescrit dans l'échange,
se souvient d'hier, n'invente jamais de consigne médicale, et produit automatiquement un
signal famille + un journal de métriques qui montre l'évolution.

## Périmètre

| ✅ Dans le périmètre (quelques heures) | ⏭️ Délibérément reporté (fast-follow / V1-V2) |
|---|---|
| Boucle conversationnelle vocale (browser STT/TTS) | Hub mains-libres « façon Alexa », proactivité matérielle |
| 1 graphe patient Graphify + interrogation par l'agent | Mémoire temporelle Graphiti + PostgreSQL |
| Structure de séance 15 min en 4 phases | Pipeline temps-réel LiveKit/Pipecat + Deepgram + ElevenLabs |
| 2-3 exercices **libres de droits** (SRT, SFA, Réminiscence) | Extraction de biomarqueurs vocaux (openSMILE) — zone R&D |
| Garde-fou détresse minimal (L1/L3/L5) + journalisation | Moteur d'escalade complet 5 niveaux fine-tuné + NeMo Guardrails |
| Signal famille vert/orange/rouge + rapport clinicien hebdo | Portail clinicien complet, co-signature électronique du tuteur, HDS |
| Tout en local (souveraineté) | Certification HDS V2.0, étude IRB, conformité MDR/EU AI Act |

> **Discipline n°1** : tout ajout hors de la colonne de gauche est *interdit* tant que la
> colonne de gauche n'est pas démontrable de bout en bout.

## Principe de latence
L'interrogation du graphe et l'écriture des souvenirs se font **en début et en fin de
séance**, jamais pendant la génération de la réponse. Le garde-fou tourne **en parallèle**
du LLM.

## Référence
Plan complet : `../Blueprint Claude Code/Plan_BLAST_Pilote_Madeleine_ClaudeCode.md`.
Aligné sur : appel du 18 juin 2026, revue de faisabilité technique, due diligence, cadre
« Orthophonie et Démence ».
