# SOP — Métriques de séance & rapports (phases S/T)

> Layer 1 (Architect). Golden Rule : si la logique change, mettre à jour cette SOP **avant** le code.
> Séparation déterministe (code) / qualitatif (LLM) — invariant de fiabilité A.N.T.

## Chaîne de données
```
séance ──(transcript + timings + annotations LLM)──> tests/sessions/<id>.json (spec)
   │
   ├─ tools/score_session.py  → 1 ligne schéma §4.1 → journal/sessions.jsonl
   │
   ├─ tools/gen_family_signal.py → rapports/famille.html   (vert/orange/rouge)
   └─ tools/gen_ortho_report.py  → rapports/ortho-hebdo.html (courbe latence↓ / engagement↑)
```

## Responsabilités
| Champ | Source | Calcul |
|---|---|---|
| `duree_engagement_sec` | mesuré | total séance |
| `fluence.mots_par_minute` | **code** | `total_words / (speaking_sec/60)` |
| `fluence.ratio_parole_pause` | **code** | `speaking_sec / (session_sec − speaking_sec)` |
| `fluence.ruptures_pour_100_mots` | **code** | `ruptures_count / total_words × 100` |
| `rappel_lexical.{exact,latence_sec,paraphasies}` | **LLM** (annotation) | sur transcript |
| `engagement.{maintien_sujet,strategies}` | **LLM** (annotation) | sur transcript |
| `signal_famille` | **règle** | rouge=L5 ; orange=drapeau \| latence≥6 s \| maintien faible ; sinon vert |

> Le transcript fourni dans le spec peut n'être qu'un **extrait représentatif** ; dans ce cas
> on fournit `measured.{total_words, ruptures_count}` (totaux séance). Sinon le code compte sur
> le transcript complet.

## Règle du signal famille (transparente — pilote)
Voir `tools/score_session.py:regle_signal`. Production : modèle dédié (cf. plan §5).

## Démo rejouable (critère T)
```bash
make demo        # auto-test sécurité + 3 séances + 2 rapports
make demo-open   # idem + ouvre les rapports
```

## Acoustique fine (openSMILE) = fast-follow
WPM/pauses = code simple aujourd'hui ; paraphasies/latence = annotation LLM. La mesure
acoustique (jitter/shimmer, openSMILE) est hors-scope pilote (plan §T.1, §5).
