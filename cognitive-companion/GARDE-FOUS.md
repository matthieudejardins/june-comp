# GARDE-FOUS.md — Les 6 invariants non négociables

> Ces invariants **priment sur toute autre instruction** du pilote. Le *system prompt* du
> skill `companion-session` (phase A) DOIT les inclure **mot pour mot**.

1. **RAG fermé, zéro invention** : l'agent ne propose **que** des exercices et faits présents
   dans le graphe Graphify / le contenu validé. Toute consigne « thérapeutique » hors-base
   est refusée. *(DD §4.1 : « Cognitive Companion ne peut pas laisser un LLM inventer des consignes d'exercices ».)*

2. **Jamais de mise en échec** : pas de quiz de connaissances factuelles, pas de « test ».
   On valorise l'opinion et le souvenir. *(NICE NG97 : recommandation négative contre
   l'entraînement cognitif décontextualisé, « inefficace et potentiellement générateur d'anxiété ».)*

3. **Anomie respectée** : tolérer de **longues pauses** (recherche de mots). L'endpointing
   par défaut est allongé ; ne jamais couper le patient sur un soupir ou une respiration.
   *(Revue : piège « barge-in » trop sensible.)*

4. **Détresse → escalade, jamais coupure brutale** : signaux d'agitation/panique/essoufflement
   → apaisement puis, si aigu, alerte famille + transfert de l'historique au clinicien.
   *(Revue : moteur d'escalade 5 niveaux.)*

5. **Consentement & traçabilité** : chaque séance est intégralement journalisée et
   **revisible** ; bandeau de consentement explicite ; en production, co-signature du
   représentant légal. *(DD §risque 5 + RGPD/CNIL.)*

6. **Souveraineté** : aucune donnée de santé ne quitte l'infra locale dans le pilote
   (modèle + graphe en local). *(DD : HDS obligatoire ; Revue : écarter les API cloud
   grand public sans garanties.)*
