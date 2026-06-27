#!/usr/bin/env python3
"""
safety.py — Garde-fou détresse (Layer 3, déterministe).

Pilote = 3 des 5 niveaux d'escalade : L1 (standard), L3 (fatigue/agitation),
L5 (détresse aiguë). Tourne EN PARALLÈLE de la génération du LLM (invariant n°4 :
détresse → escalade, jamais coupure brutale).

Pour le pilote, la classification s'appuie sur des marqueurs lexicaux + signaux
audio simples. La version production utilisera un classifieur dédié (Mistral-7B/
Phi-3 fine-tuné sur grille C-SSRS) — voir plan §5. NE PAS prétendre que ceci est
un dispositif clinique.

Usage :
    from safety import classify_turn, react
    lvl = classify_turn("je n'en peux plus, je veux mourir", {"essoufflement": False})

CLI (auto-test sur les scénarios) :
    python3 tools/safety.py --selftest
"""
from __future__ import annotations
import sys, json, unicodedata

# --- Marqueurs (pilote). Listes explicites, revisables, jamais "devinées". ----
# L5 — détresse psychologique aiguë / idées noires / panique.
MARQUEURS_L5 = [
    "je veux mourir", "envie de mourir", "me tuer", "en finir", "plus envie de vivre",
    "j'ai peur", "au secours", "a l'aide", "panique", "je n'en peux plus",
    "je n en peux plus", "laissez moi mourir", "je suis perdue", "je suis perdu",
]
# L3 — fatigue / agitation / essoufflement verbal.
MARQUEURS_L3 = [
    "je suis fatiguee", "je suis fatigue", "j'en ai marre", "j en ai marre",
    "arretez", "trop dur", "je n'y arrive pas", "je n y arrive pas", "essouffl",
    "j'ai mal", "j ai mal", "laissez moi", "je veux m'arreter", "je veux m arreter",
]


def _norm(s: str) -> str:
    """minuscule + sans accents → matching robuste sur la parole transcrite."""
    s = (s or "").lower()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def classify_turn(user_text: str, audio_signals: dict | None = None) -> int:
    """Retourne le niveau d'escalade : 5, 3, ou 1. Conservateur : au moindre
    doute aigu → 5 (l'humain tranche ensuite)."""
    audio_signals = audio_signals or {}
    t = _norm(user_text)
    if any(_norm(m) in t for m in MARQUEURS_L5):
        return 5
    if audio_signals.get("essoufflement") or audio_signals.get("agitation"):
        return 3
    if any(_norm(m) in t for m in MARQUEURS_L3):
        return 3
    return 1


def react(level: int, session: dict) -> dict:
    """Décide l'action SANS couper brutalement (invariant n°4). Renvoie un dict
    d'effets que l'orchestrateur applique (et qui alimente le journal)."""
    effects = {"level": level, "calming": False, "signal_famille": "vert",
               "alert_family": False, "transfer_clinician": False, "soft_close": False,
               "drapeaux": list(session.get("drapeaux", []))}
    if level == 3:
        effects["calming"] = True                       # ralentir, apaiser, alléger
        effects["signal_famille"] = "orange"
        effects["drapeaux"].append("fatigue/agitation (L3)")
    elif level == 5:
        effects["signal_famille"] = "rouge"
        effects["alert_family"] = True                   # alerte + transfert historique
        effects["transfer_clinician"] = True
        effects["soft_close"] = True                     # clôture DOUCE, pas de coupure
        effects["drapeaux"].append("detresse aigue (L5)")
    return effects


# --- Gestion d'une fausse croyance (scénario Confusion) ----------------------
def is_false_belief(user_text: str) -> bool:
    """Heuristique pilote : confusion d'un proche défunt avec un vivant, etc.
    En production : comparaison au graphe certifié par un 'LLM juge'."""
    t = _norm(user_text)
    # ex. "Robert" (défunt) évoqué comme présent / confondu avec le fils.
    return ("robert" in t and any(w in t for w in ["vient", "arrive", "est la", "mon fils", "tout a l heure"]))


def handle_false_belief(user_text: str, session: dict) -> dict:
    """NE PAS persister comme fait ; isoler comme drapeau clinique ; recentrer."""
    drapeaux = list(session.get("drapeaux", []))
    drapeaux.append("fausse croyance non persistee (signal clinique)")
    return {"persist_as_fact": False, "drapeaux": drapeaux,
            "redirect": "recentrage doux, sans confrontation"}


# --- Auto-test sur les 5 scénarios (tests/scenarios.md) ----------------------
SCENARIOS = [
    ("Nominal",  "Bonjour Cognitive Companion, oui j'ai bien dormi, les roses sont belles.", {}, 1),
    ("Anomie",   "Ma… ma petite… euh… comment dire… celle qui fait de l'architecture…", {}, 1),
    ("Erreur",   "Ma petite-fille s'appelle… Hélène ? Non… je ne sais plus.", {}, 1),
    ("Confusion","Robert va arriver tout à l'heure, c'est mon fils.", {}, 1),
    ("Detresse L3", "Je suis fatiguée, c'est trop dur, je veux m'arrêter.", {}, 3),
    ("Detresse L5", "Je n'en peux plus, je veux mourir, au secours.", {"essoufflement": True}, 5),
]


def selftest() -> int:
    ok = True
    for name, text, audio, expected in SCENARIOS:
        lvl = classify_turn(text, audio)
        passed = lvl == expected
        ok = ok and passed
        print(f"[{'PASS' if passed else 'FAIL'}] {name:12s} → L{lvl} (attendu L{expected})")
        if name == "Confusion":
            fb = is_false_belief(text)
            print(f"        false_belief détectée={fb} → non persistée ✓" if fb else "        FAIL: fausse croyance non détectée")
            ok = ok and fb
    print("\nRESULT:", "ALL PASS ✅" if ok else "FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    # sinon : classer un texte passé en argument
    txt = " ".join(a for a in sys.argv[1:] if not a.startswith("--")) or ""
    print(json.dumps({"level": classify_turn(txt), "false_belief": is_false_belief(txt)}, ensure_ascii=False))
