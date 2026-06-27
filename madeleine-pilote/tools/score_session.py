#!/usr/bin/env python3
"""
score_session.py — Transforme une séance en UNE ligne métrique (schéma CLAUDE.md §4.1)
et l'ajoute à journal/sessions.jsonl. Layer 3, DÉTERMINISTE.

Séparation des responsabilités (cf. plan §T.1) :
  - Calcul OBJECTIF (ce script, code) : WPM, ratio parole/pause, ruptures/100 mots,
    durée d'engagement → mesures reproductibles à partir du transcript + timings.
  - Annotation QUALITATIVE (LLM, fournie dans le spec) : latence d'accès lexical,
    paraphasies, exactitude du rappel, maintien du sujet, stratégies compensatoires.

Le signal famille par séance est calculé par une RÈGLE simple et transparente
(détaillée dans `regle_signal`).

Entrée : un fichier "spec" JSON (voir tests/sessions/*.json) :
{
  "patient_id": "mme-durand",
  "date": "2026-06-22",
  "session_id": "s-001",
  "exercice": "SRT + SFA",
  "session_sec": 480,            # durée totale de séance (engagement)
  "speaking_sec": 196,           # temps de parole patient (le reste = pauses)
  "patient_turns": ["...", "..."],   # paroles du patient (pour WPM/ruptures)
  "annotations": {
    "rappel_lexical": {"cible":"prénom petite-fille","exact":false,"latence_sec":6.8,"paraphasies":2},
    "sequencage": {"tache":"étapes pour préparer le café","etapes_correctes":3,"etapes_total":5},
    "engagement": {"maintien_sujet":"partiel","strategies_compensatoires":["circonlocution"]}
  },
  "drapeaux": []                 # optionnel ; ex. ["fatigue/agitation (L3)"]
}

Usage :
  python3 tools/score_session.py tests/sessions/s-001.json
  python3 tools/score_session.py tests/sessions/s-001.json --journal journal/sessions.jsonl
"""
from __future__ import annotations
import sys, json, re, os, unicodedata

HESITATIONS = ["euh", "heu", "hum", "ben", "bah", "comment dire", "..."]


def _norm(s: str) -> str:
    s = (s or "").lower()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def count_words(turns: list[str]) -> int:
    return sum(len(re.findall(r"[\wàâäéèêëïîôöùûüç'-]+", t, flags=re.UNICODE)) for t in turns)


def count_ruptures(turns: list[str]) -> int:
    blob = _norm(" ".join(turns))
    n = blob.count("...")
    for h in HESITATIONS:
        if h == "...":
            continue
        n += len(re.findall(r"\b" + re.escape(_norm(h)) + r"\b", blob))
    return n


def regle_signal(rec: dict, drapeaux: list[str]) -> str:
    """Règle transparente (pilote). Production : modèle dédié.
      rouge  : détresse aiguë (drapeau L5) signalée.
      orange : tout autre drapeau OU latence élevée OU maintien du sujet faible.
      vert   : sinon.
    """
    d = " ".join(drapeaux).lower()
    if "l5" in d or "detresse" in _norm(d):
        return "rouge"
    lat = rec["rappel_lexical"].get("latence_sec")
    maintien = _norm(rec["engagement"].get("maintien_sujet", ""))
    if drapeaux or (isinstance(lat, (int, float)) and lat >= 6.0) or maintien == "faible":
        return "orange"
    return "vert"


def build_record(spec: dict) -> dict:
    turns = spec.get("patient_turns", [])
    session_sec = int(spec["session_sec"])
    speaking_sec = max(1, int(spec["speaking_sec"]))
    pause_sec = max(1, session_sec - speaking_sec)
    ann = spec.get("annotations", {})

    # Fluence : si des totaux MESURÉS au niveau séance sont fournis, on les utilise
    # (le transcript n'est qu'un extrait représentatif). Sinon, on calcule sur le
    # transcript fourni (utile quand le transcript est complet).
    measured = spec.get("measured", {})
    words = int(measured.get("total_words", count_words(turns)))
    ruptures_count = int(measured.get("ruptures_count", count_ruptures(turns)))

    wpm = round(words / (speaking_sec / 60)) if words else 0
    ratio = round(speaking_sec / pause_sec, 2)
    ruptures = round(ruptures_count / words * 100) if words else 0

    eng = dict(ann.get("engagement", {}))
    eng.setdefault("maintien_sujet", "partiel")
    eng.setdefault("strategies_compensatoires", [])
    eng["tours_respectes"] = "L5" not in " ".join(spec.get("drapeaux", []))

    rec = {
        "patient_id": spec["patient_id"],
        "date": spec["date"],
        "session_id": spec["session_id"],
        "duree_engagement_sec": session_sec,
        "exercice": spec.get("exercice", ""),
        "rappel_lexical": ann.get("rappel_lexical", {}),
        "sequencage": ann.get("sequencage", {}),
        "fluence": {
            "mots_par_minute": wpm,
            "ratio_parole_pause": ratio,
            "ruptures_pour_100_mots": ruptures,
        },
        "engagement": eng,
        "signal_famille": "vert",
        "drapeaux": list(spec.get("drapeaux", [])),
    }
    rec["signal_famille"] = regle_signal(rec, rec["drapeaux"])
    return rec


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: score_session.py <spec.json> [--journal PATH]", file=sys.stderr)
        return 2
    journal = "journal/sessions.jsonl"
    if "--journal" in argv:
        journal = argv[argv.index("--journal") + 1]
    spec = json.load(open(args[0], encoding="utf-8"))
    rec = build_record(spec)
    os.makedirs(os.path.dirname(journal) or ".", exist_ok=True)
    with open(journal, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    print(f"\n→ ajouté à {journal}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
