# exercices.md — Base FERMÉE d'exercices (libres de droits)

> **RAG fermé** : l'agent ne propose QUE des exercices listés ici. Aucune consigne hors-base.
> On s'inspire des *principes* (SRT, SFA, réminiscence) sans copier les manuels protégés
> (CST/UCL, batteries propriétaires type MoCA/MMSE/DO 80).

## 1. Récupération Espacée Sans Erreur (SRT / EL)
- **But** : faire rappeler un fait fonctionnel (prénom d'un proche, un rdv) en **intervalles
  doublants** : 5 s, 10 s, 20 s, 30 s, 1 min, 2 min…
- Utiliser le **vocabulaire du patient**.
- En cas d'erreur : indiçage immédiat, **aucune** rétroaction négative (errorless).
- **Métriques** : `rappel_lexical` (exact, latence_sec, paraphasies).

## 2. Analyse Sémantique des Traits (SFA) — pour l'anomie
- **But** : guider la description d'un mot manquant via la chaîne :
  catégorie → fonction → propriétés physiques → localisation → associations.
- Réactive l'accès lexical sans jamais « tester ».
- **Métriques** : `fluence`, `engagement.strategies_compensatoires`.

## 3. Réminiscence (RT)
- **But** : évocation thématique guidée d'un souvenir d'enfance/métier (preuves Cochrane),
  éventuellement appuyée par une photo de `patients/<id>/media/`.
- **Opinions et souvenirs** uniquement, jamais de connaissances factuelles à vérifier.
- **Métriques** : `duree_engagement_sec`, `engagement.maintien_sujet`.

---
## À PROSCRIRE (NICE NG97)
L'« entraînement cognitif » décontextualisé (exercices isolés répétitifs type brain-training)
— inefficace et anxiogène. Madeleine est une **stimulation conversationnelle**, pas un jeu de mémoire.
