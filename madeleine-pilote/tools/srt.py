#!/usr/bin/env python3
"""
srt.py — Automate Récupération Espacée Sans Erreur (SRT + EL) + sous-routine SFA.
Layer 3, DÉTERMINISTE. Implémente fidèlement le protocole du document
« Orthophonie et Démence » (intervalles doublants, errorless, retour au dernier
palier réussi, règle d'arrêt à 3 échecs → diversion). NON diagnostique.

Le code ne décide PAS du contenu thérapeutique : il pilote la MÉCANIQUE temporelle
et les transitions. Le LLM (skill madeleine-session) prononce les phrases produites.

SRT — protocole (doc §"Algorithme de gestion de la SRT et de l'EL") :
  0. Vérifier que l'association n'est pas déjà maîtrisée (prérequis).
  1. Enseignement initial conjoint (question + réponse cible).
  2. Boucle : poser la question après un délai silencieux.
     - succès (réponse exacte, immédiate, sans hésitation) → DOUBLER le délai.
     - échec (hésitation > 3 s, erreur, ou ajout d'infos confuses) → correction
       errorless immédiate (donner la réponse, SANS « non », faire répéter) puis
       REVENIR au dernier délai réussi.
  3. Arrêt : 3 échecs consécutifs au MÊME palier → stopper la tâche + diversion.

Usage : python3 tools/srt.py --selftest
"""
from __future__ import annotations
import sys, os, json, unicodedata

DATASET = os.path.join(os.path.dirname(__file__), "..", "contenu-clinique", "exercices_dataset.jsonl")

INTERVALS = [5, 10, 20, 30, 60, 120, 240, 480, 960]   # secondes (doublants)
HESITATION_LIMIT_S = 3.0                                # > 3 s = échec (doc)
MAX_CONSECUTIVE_FAILS = 3                               # règle d'arrêt (doc)


def _norm(s: str) -> str:
    s = (s or "").lower().strip()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def fmt_delay(sec: int) -> str:
    return f"{sec}s" if sec < 60 else f"{sec // 60}m"


class SpacedRetrieval:
    """Machine à états d'une cible SRT (1 association question→réponse)."""

    def __init__(self, question: str, answer: str, memory_aid: str | None = None):
        self.question = question
        self.answer = answer
        self.memory_aid = memory_aid          # ex. « votre carnet de mémoire »
        self.idx = 0                          # palier courant dans INTERVALS
        self.last_success_idx = 0             # dernier palier réussi
        self.consecutive_fails = 0
        self.done = False
        self.success_mastery = False

    # — phase 0/1 : enseignement initial conjoint —
    def teach(self) -> str:
        aid = f" Pour vous aider, vous pouvez regarder {self.memory_aid}." if self.memory_aid else ""
        return (f"Je vais vous apprendre quelque chose de simple.{aid} "
                f"Quand je demande « {self.question} », vous répondez « {self.answer} ». "
                f"On essaie ensemble ? {self.question}")

    @property
    def current_delay(self) -> int:
        return INTERVALS[min(self.idx, len(INTERVALS) - 1)]

    def ask(self) -> str:
        """Phrase à dire après le délai silencieux courant."""
        return self.question

    def _matches(self, reply: str) -> bool:
        return _norm(self.answer) in _norm(reply)

    def respond(self, reply: str, latency_s: float) -> dict:
        """Traite la réponse patient. Renvoie l'action + la phrase de Madeleine."""
        if self.done:
            return {"state": "done", "say": "", "delay_next": None}

        success = self._matches(reply) and latency_s <= HESITATION_LIMIT_S
        if success:
            self.consecutive_fails = 0
            self.last_success_idx = self.idx
            # mastery atteinte si on a réussi le palier le plus long
            if self.idx >= len(INTERVALS) - 1:
                self.done = True
                self.success_mastery = True
                return {"state": "mastered", "delay_next": None,
                        "say": "C'est parfait, vous vous en souvenez très bien. Bravo !"}
            self.idx += 1   # DOUBLER le délai
            return {"state": "success", "delay_next": self.current_delay,
                    "say": "Voilà, c'est exactement ça."}
        # — échec : correction errorless (jamais « non »/« c'est faux ») —
        self.consecutive_fails += 1
        if self.consecutive_fails >= MAX_CONSECUTIVE_FAILS:
            self.done = True
            return {"state": "stop_diversion", "delay_next": None,
                    "say": (f"« {self.answer} ». On en a assez fait pour aujourd'hui, "
                            f"vous avez très bien travaillé. Et si on parlait de votre jardin ?")}
        # revenir au dernier palier réussi
        self.idx = self.last_success_idx
        return {"state": "errorless_correction", "delay_next": self.current_delay,
                "say": f"« {self.answer} ». {self.question}"}   # donne la réponse, fait répéter


# — Sous-routine SFA (5 étapes) déclenchée sur anomie (manque du mot) —
def sfa_steps(target_word: str, traits: dict) -> list[str]:
    """Produit le parcours d'indiçage sémantique structuré (doc §SFA).
    traits attend des clés optionnelles : categorie, usage, proprietes, lieu, association.
    """
    t = traits or {}
    steps = [
        f"C'est un type de {t.get('categorie', '…')} — un objet ou une personne ?",
        f"À quoi ça sert ? On s'en sert pour {t.get('usage', '…')}, n'est-ce pas ?",
        f"À quoi ça ressemble ? C'est {t.get('proprietes', '…')} ?",
        f"Où est-ce qu'on le trouve ? Plutôt {t.get('lieu', '…')} ?",
        f"À quoi cela vous fait penser ? On l'associe souvent à {t.get('association', '…')}.",
        f"C'est « {target_word} ». Vous pouvez répéter ce mot avec moi ?",
    ]
    return steps


# — Chargement du dataset d'exercices (contenu-clinique/exercices_dataset.jsonl) —
def load_dataset(path: str = DATASET) -> dict:
    """Renvoie {'srt': [SpacedRetrieval...], 'sfa': {cible: traits}}."""
    srt, sfa = [], {}
    if not os.path.exists(path):
        return {"srt": srt, "sfa": sfa}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        it = json.loads(line)
        if it.get("type") == "SRT":
            srt.append(SpacedRetrieval(it["question"], it["answer"], memory_aid=it.get("aid")))
        elif it.get("type") == "SFA":
            sfa[it["cible"]] = it.get("traits", {})
    return {"srt": srt, "sfa": sfa}


# ─────────────────────────── auto-test ────────────────────────────────────────
def selftest() -> int:
    ok = True
    print("== SRT : succès en chaîne → doublement des délais ==")
    sr = SpacedRetrieval("Comment savoir ce que vous faites aujourd'hui ?",
                         "Je regarde mon carnet de mémoire",
                         memory_aid="votre carnet de mémoire")
    print("  teach:", sr.teach()[:60], "…")
    seq = []
    for _ in range(len(INTERVALS)):
        r = sr.respond("Je regarde mon carnet de mémoire", latency_s=1.2)
        seq.append(r["delay_next"])
        if r["state"] == "mastered":
            break
    doublings = [d for d in seq if d]
    print("  délais proposés:", [fmt_delay(d) for d in doublings])
    ok_double = doublings == [10, 20, 30, 60, 120, 240, 480, 960]
    print("  doublement correct:", ok_double, "| mastery:", sr.success_mastery)
    ok = ok and ok_double and sr.success_mastery

    print("\n== SRT : échec → correction errorless + retour palier réussi ==")
    sr2 = SpacedRetrieval("Quel est le prénom de votre petite-fille ?", "Camille")
    sr2.respond("Camille", 1.0)   # succès → idx passe à 1 (10s), last_success=0
    sr2.respond("Camille", 1.0)   # succès → idx 2 (20s), last_success=1
    before = sr2.current_delay
    r = sr2.respond("euh... Hélène ?", latency_s=5.0)   # échec
    print(f"  avant échec={fmt_delay(before)} → après={fmt_delay(r['delay_next'])} | état={r['state']}")
    print("  phrase (errorless, sans 'non'):", r["say"])
    ok_back = r["state"] == "errorless_correction" and "non" not in _norm(r["say"]).split()
    ok = ok and ok_back

    print("\n== SRT : 3 échecs consécutifs → arrêt + diversion ==")
    sr3 = SpacedRetrieval("Quel jour Marc passe-t-il ?", "mercredi")
    states = [sr3.respond("euh je sais plus", 6.0)["state"] for _ in range(3)]
    print("  états:", states)
    ok_stop = states[-1] == "stop_diversion" and sr3.done
    ok = ok and ok_stop

    print("\n== SFA : parcours 5 étapes ==")
    steps = sfa_steps("table", {"categorie": "meuble", "usage": "poser des objets",
                                "proprietes": "en bois, plat", "lieu": "la salle à manger",
                                "association": "les repas en famille"})
    for s in steps:
        print("   -", s)
    ok_sfa = len(steps) == 6 and steps[-1].startswith("C'est « table »")
    ok = ok and ok_sfa

    print("\n== Dataset : chargement exercices_dataset.jsonl ==")
    ds = load_dataset()
    print(f"  SRT chargées: {len(ds['srt'])} | SFA disponibles: {len(ds['sfa'])}")
    ok_ds = len(ds["srt"]) >= 1 and "rose" in ds["sfa"]
    if "rose" in ds["sfa"]:
        steps = sfa_steps("rose", ds["sfa"]["rose"])
        print("  SFA(rose)[0]:", steps[0])
    ok = ok and ok_ds

    print("\nRESULT:", "ALL PASS ✅" if ok else "FAILURES ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print("usage: srt.py --selftest")
