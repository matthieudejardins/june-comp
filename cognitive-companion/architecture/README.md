# architecture/ — Layer 1 (SOP techniques)

> **Golden Rule** : si la logique change, on met à jour la SOP **ici, avant** le code.

SOP à rédiger lors des phases L → T (une par brique) :
- `SOP-hermes-setup.md` — install Hermes + config `~/.hermes/config.yaml` + fix `num_ctx=64000`.
- `SOP-graphify.md` — build du graphe patient + serveur MCP (query_graph/get_neighbors/...).
- `SOP-seance.md` — orchestration d'une séance (lecture graphe → 4 phases → écriture journal).
- `SOP-garde-fou-detresse.md` — classifieur L1/L3/L5 en thread parallèle + actions.
- `SOP-rapports.md` — agrégation journal → signal famille + rapport ortho (courbe).
