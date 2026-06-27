#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# sovereignty_check.sh — Audit de souveraineté (invariant n°6).
# Lit la posture ACTUELLE (cerveau + voix) et dit si on est prêt pour un
# patient RÉEL (tout local) ou seulement pour le PROTO fictif (cloud OK).
# Ne modifie RIEN. Lecture seule.
# ─────────────────────────────────────────────────────────────────────────
set -uo pipefail
cfg="$HOME/.hermes/config.yaml"
green="\033[32m"; red="\033[31m"; yellow="\033[33m"; off="\033[0m"

echo "▎ Audit de souveraineté — pilote Cognitive Companion"
echo

# 1) Cerveau (LLM)
provider=$(grep -E '^\s*provider:' "$cfg" 2>/dev/null | head -1 | awk '{print $2}')
base=$(grep -E '^\s*base_url:' "$cfg" 2>/dev/null | head -1 | awk '{print $2}')
brain_local=0
case "$base" in
  *127.0.0.1*|*localhost*) [[ "$provider" == "ollama" || "$base" == *11434* ]] && brain_local=1 ;;
esac
echo "1. CERVEAU (LLM)"
echo "   provider=$provider  base_url=$base"
if [[ "$base" == *8765* ]]; then
  echo -e "   ${yellow}⚠ Gemini via rotateur local (clés cloud) → cerveau = CLOUD${off}"
elif [[ "$brain_local" == 1 ]]; then
  echo -e "   ${green}✓ modèle local (Ollama) → cerveau = LOCAL${off}"
else
  echo -e "   ${yellow}⚠ endpoint non local → cerveau = CLOUD${off}"
fi

# 2) Voix
echo "2. VOIX"
obu="${OPENAI_BASE_URL:-https://api.openai.com}"
if [[ "$obu" == *localhost* || "$obu" == *127.0.0.1* ]]; then
  echo -e "   OPENAI_BASE_URL=$obu → ${green}✓ moteur voix LOCAL${off}"
else
  echo -e "   OPENAI_BASE_URL=$obu → ${yellow}⚠ voix = OpenAI Realtime (CLOUD)${off}"
fi

# 3) Pré-requis locaux disponibles ?
echo "3. PRÉ-REQUIS LOCAUX"
command -v ollama >/dev/null && echo -e "   ${green}✓ ollama installé${off}" || echo -e "   ${red}✗ ollama ABSENT${off} (cerveau local impossible tant qu'il manque)"
command -v whisper-server >/dev/null 2>&1 || command -v piper >/dev/null 2>&1 \
  && echo -e "   ${green}✓ moteur STT/TTS local détecté${off}" \
  || echo -e "   ${red}✗ aucun moteur voix local (faster-whisper/Piper) détecté${off}"

echo
echo "▎ VERDICT"
if [[ "$brain_local" == 1 && ( "$obu" == *localhost* || "$obu" == *127.0.0.1* ) ]]; then
  echo -e "   ${green}SOUVERAIN — prêt pour un patient RÉEL (invariant n°6 satisfait).${off}"
else
  echo -e "   ${yellow}NON souverain — OK uniquement pour le PROTO (patient FICTIF).${off}"
  echo "   Avant tout patient réel : voir architecture/SOP-souverainete-local.md"
fi
