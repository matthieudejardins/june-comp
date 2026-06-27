#!/usr/bin/env python3
"""
build_exercise_dataset.py — Construit contenu-clinique/exercices_dataset.jsonl.

Deux types d'items, alimentant tools/srt.py :
  - "SRT" : cibles de récupération espacée (question→réponse cible + aide),
            DÉRIVÉES du dossier patient (carnet-de-memoire.md / graphe) → 100 %
            personnalisées et dans le corpus fermé du patient.
  - "SFA" : items d'analyse sémantique des traits (mot-cible + 5 traits), curés
            à la main sur l'univers du patient (jardin, cuisine, famille, Loire).

Honnêteté des sources (skill phd) :
  - On ne FABRIQUE PAS de fréquences lexicales. Le champ `freq_lexique` reste null ;
    la calibration de difficulté se fait via **Lexique.org** (table freqlemfilms2 /
    freqlivres, Lexique 3.83, CC) en jointure ultérieure — documenté ci-dessous.
  - `difficulte` est qualitative et justifiable (imageabilité + longueur + familiarité).

Usage : python3 tools/build_exercise_dataset.py
        python3 tools/build_exercise_dataset.py --patient patients/mme-durand
"""
from __future__ import annotations
import sys, os, json, re

# — SFA : items curés sur l'univers de la patiente (concrets, imageables, errorless) —
SFA_ITEMS = [
    ("rose", "fleur", "décorer, offrir, sentir", "colorée, parfumée, à tige épineuse",
     "le jardin", "l'amour, le printemps", "jardin", "facile"),
    ("sécateur", "outil", "couper les tiges et les branches", "métallique, à deux lames, tenu en main",
     "le jardin, la remise", "le jardinage, les rosiers", "jardin", "moyen"),
    ("arrosoir", "outil", "arroser les plantes", "en métal ou plastique, avec un bec et une anse",
     "le jardin", "l'eau, les fleurs", "jardin", "moyen"),
    ("tarte", "plat sucré", "se manger en dessert", "ronde, dorée, garnie de fruits",
     "la cuisine", "le dimanche, la tarte Tatin", "cuisine", "facile"),
    ("cafetière", "ustensile", "préparer le café", "avec un filtre et un réservoir d'eau",
     "la cuisine", "le café du matin", "cuisine", "moyen"),
    ("four", "appareil", "cuire les plats", "chaud, rectangulaire, avec une porte",
     "la cuisine", "la cuisson, la tarte", "cuisine", "facile"),
    ("cahier", "objet", "écrire et apprendre", "rectangulaire, à pages lignées",
     "l'école, le bureau", "l'écriture, les élèves", "école", "facile"),
    ("livre", "objet", "lire et apprendre", "à pages reliées, avec une couverture",
     "la bibliothèque, l'école", "la lecture, les histoires", "école", "facile"),
    ("rivière", "lieu naturel", "y voir couler l'eau, s'y promener", "longue, sinueuse, avec de l'eau qui coule",
     "la campagne", "la Loire, les promenades", "loire", "moyen"),
    ("train", "moyen de transport", "voyager d'une ville à l'autre", "long, sur des rails, avec des wagons",
     "la gare", "les voyages, Nantes, Paris", "famille", "facile"),
]

# Cibles SRT par défaut si le carnet n'est pas lisible (corpus patient).
SRT_FALLBACK = [
    ("Comment savoir ce que je fais aujourd'hui ?", "Je regarde mon carnet de mémoire", "le carnet", "facile"),
    ("Quel est le prénom de ma petite-fille ?", "Camille", "fiche Camille", "moyen"),
    ("Quel jour Marc passe-t-il ?", "Le mercredi", "fiche Marc", "moyen"),
]

LEXIQUE_NOTE = ("curated; difficulté qualitative (imageabilité+familiarité). "
                "Calibration fréquence → Lexique.org freqlemfilms2 (Lexique 3.83, CC) en jointure ultérieure.")


def parse_carnet_srt(patient_dir: str):
    """Extrait les cibles SRT du tableau de carnet-de-memoire.md si présent."""
    p = os.path.join(patient_dir, "carnet-de-memoire.md")
    if not os.path.exists(p):
        return []
    rows = []
    for line in open(p, encoding="utf-8"):
        # lignes de tableau markdown : | « question » | « réponse » | aide |
        if line.count("|") >= 3 and "«" in line:
            cells = [c.strip().strip("«»").strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 3 and "Question" not in cells[0]:
                rows.append((cells[0], cells[1], cells[2], "moyen"))
    return rows


def main(argv):
    patient_dir = "patients/mme-durand"
    if "--patient" in argv:
        patient_dir = argv[argv.index("--patient") + 1]
    out = "contenu-clinique/exercices_dataset.jsonl"

    srt = parse_carnet_srt(patient_dir) or SRT_FALLBACK
    items = []
    for i, (q, a, aid, diff) in enumerate(srt, 1):
        items.append({
            "type": "SRT", "id": f"srt-{i:02d}", "question": q, "answer": a,
            "aid": aid, "theme": "patient", "difficulte": diff,
            "source": f"corpus patient ({patient_dir}/carnet-de-memoire.md)"
        })
    for w, cat, usage, prop, lieu, asso, theme, diff in SFA_ITEMS:
        items.append({
            "type": "SFA", "id": f"sfa-{w}", "cible": w,
            "traits": {"categorie": cat, "usage": usage, "proprietes": prop,
                       "lieu": lieu, "association": asso},
            "theme": theme, "difficulte": diff, "freq_lexique": None,
            "source": LEXIQUE_NOTE
        })

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    n_srt = sum(1 for it in items if it["type"] == "SRT")
    n_sfa = sum(1 for it in items if it["type"] == "SFA")
    print(f"→ {out} : {n_srt} cibles SRT + {n_sfa} items SFA = {len(items)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
