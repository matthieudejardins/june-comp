#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# demo.sh — Démo d'évolution rejouable EN UNE COMMANDE (critère T).
# Repart de zéro, rejoue 3 séances simulées, régénère signal famille + rapport
# orthophoniste (avec courbe), et lance l'auto-test du garde-fou détresse.
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail
cd "$(dirname "$0")"

JOURNAL="journal/sessions.jsonl"

echo "▎ 0. Garde-fou détresse — auto-test des 5 scénarios (phase S)"
python3 tools/safety.py --selftest
echo

echo "▎ 1. Réinitialisation du journal"
: > "$JOURNAL"

echo "▎ 2. Scoring des 3 séances simulées (transcript → métriques → journal)"
for s in tests/sessions/s-001.json tests/sessions/s-002.json tests/sessions/s-003.json; do
  python3 tools/score_session.py "$s" --journal "$JOURNAL" >/dev/null
  echo "   ✓ $(basename "$s")"
done
echo "   → $(wc -l < "$JOURNAL" | tr -d ' ') lignes dans $JOURNAL"
echo

echo "▎ 3. Signal famille (vert/orange/rouge)"
python3 tools/gen_family_signal.py --journal "$JOURNAL" --out rapports/famille.html

echo "▎ 4. Rapport orthophoniste hebdo (avec courbe d'évolution)"
python3 tools/gen_ortho_report.py --journal "$JOURNAL" --out rapports/ortho-hebdo.html
echo

echo "✅ Démo prête :"
echo "   - rapports/famille.html"
echo "   - rapports/ortho-hebdo.html"
[ "${OPEN:-0}" = "1" ] && command -v open >/dev/null && open rapports/ortho-hebdo.html rapports/famille.html || true
