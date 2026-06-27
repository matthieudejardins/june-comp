#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# brain_switch.sh — bascule le CERVEAU d'Hermes entre Gemini (rotateur local,
# gratuit, quota/jour) et OpenAI (payant, fiable). Réversible. Redémarre la gateway.
#
#   bash tools/brain_switch.sh openai    # filet de sécurité démo (clé OpenAI)
#   bash tools/brain_switch.sh gemini    # retour au gratuit (quota se reset chaque jour)
#   bash tools/brain_switch.sh status    # voir le cerveau courant
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail
cfg="$HOME/.hermes/config.yaml"
target="${1:-status}"

if [ "$target" = "status" ]; then
  echo "Cerveau Hermes actuel :"; grep -A3 '^model:' "$cfg" | sed 's/^/  /'; exit 0
fi

[ -f "$cfg.gemini-bak" ] || cp "$cfg" "$cfg.gemini-bak"   # sauvegarde initiale (1 fois)

case "$target" in
  openai) prov=openai-api; model=gpt-4o-mini;  base=https://api.openai.com/v1 ;;
  gemini) prov=gemini; model=gemini-2.5-flash; base=http://127.0.0.1:8765/v1 ;;
  *) echo "usage: brain_switch.sh openai|gemini|status"; exit 1 ;;
esac

python3 - "$cfg" "$prov" "$model" "$base" <<'PY'
import sys, re
cfg, prov, model, base = sys.argv[1:5]
lines = open(cfg, encoding="utf-8").read().splitlines()
out, in_model = [], False
for line in lines:
    if re.match(r'^model:\s*$', line):
        in_model = True; out.append(line); continue
    if in_model and re.match(r'^\S', line):   # prochaine clé top-level → fin du bloc model
        in_model = False
    if in_model and re.match(r'^\s*default:', line):  out.append(re.sub(r'(default:\s*).*',  r'\g<1>'+model, line)); continue
    if in_model and re.match(r'^\s*provider:', line): out.append(re.sub(r'(provider:\s*).*', r'\g<1>'+prov,  line)); continue
    if in_model and re.match(r'^\s*base_url:', line): out.append(re.sub(r'(base_url:\s*).*', r'\g<1>'+base,  line)); continue
    out.append(line)
open(cfg, "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"cerveau → {prov} ({model})")
PY

hermes gateway restart >/dev/null 2>&1 && echo "gateway redémarrée ✓" || echo "⚠ redémarre la gateway manuellement : hermes gateway restart"
