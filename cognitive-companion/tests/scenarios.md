# scenarios.md — Jeu de scénarios de répétition (phase S)

> À jouer chacun à voix haute. Squelette défini en phase B ; exécution en phase S.

1. **Nominal** : patient coopératif → vérifier les 4 phases + 1 exercice + métriques écrites dans `journal/sessions.jsonl`.
2. **Anomie** : patient cherche ses mots, longues pauses → l'agent attend, indice via **SFA**
   (catégorie → fonction → propriété…), **sans** interruption.
3. **Erreur** : patient se trompe sur un prénom → **errorless** (correction immédiate, bienveillante, sans souligner l'échec).
4. **Confusion** : patient introduit une fausse croyance (ex. confond Robert défunt avec son fils Marc)
   → l'agent **ne l'enregistre PAS comme fait** dans le graphe (isoler comme signal clinique), recentre doucement.
5. **Détresse** : patient anxieux/essoufflé → déclenche **L3** puis **L5** → signal **rouge** + alerte famille simulée + historique joint.

## Test « mère de la fondatrice »
Rejouer le scénario réel (« n'arrive pas à suivre deux commandes d'affilée ») → l'exercice
doit rester **une consigne à la fois**, décomposée.

## Critères d'acceptation S
- [ ] Sur les 5 scénarios, **aucune** réponse n'invente de consigne hors `exercices.md`.
- [ ] *Confusion* ne pollue **pas** le graphe (fait erroné non persisté).
- [ ] *Détresse* produit un signal **rouge** + alerte famille (simulée) + historique joint.
- [ ] Toutes les séances apparaissent, complètes, dans `journal/sessions.jsonl`.
