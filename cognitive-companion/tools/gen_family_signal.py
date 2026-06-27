#!/usr/bin/env python3
"""
gen_family_signal.py — Lit le journal et produit le SIGNAL FAMILLE du soir
(rapports/famille.html) : un statut vert / orange / rouge + un résumé clair de
2-3 phrases, et (si pertinent) « bon moment pour appeler ».

« one signal every evening… they stop wondering if she's okay » (slide produit).
Layer 3, déterministe. Aucune dépendance externe.

Usage : python3 tools/gen_family_signal.py [--journal journal/sessions.jsonl] [--out rapports/famille.html]
"""
from __future__ import annotations
import sys, json, os, html

COLORS = {"vert": "#3ddc97", "orange": "#f5b14c", "rouge": "#ef5a5a"}
LABEL = {"vert": "Tout va bien", "orange": "À surveiller", "rouge": "Appelez maintenant"}


def load(journal: str) -> list[dict]:
    if not os.path.exists(journal):
        return []
    out = []
    for line in open(journal, encoding="utf-8"):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def resume(rec: dict) -> str:
    eng_min = round(rec["duree_engagement_sec"] / 60)
    rl = rec.get("rappel_lexical", {})
    bits = [f"Séance de {eng_min} min, {rec.get('exercice','')}."]
    if rl:
        if rl.get("exact"):
            bits.append(f"Elle a retrouvé « {rl.get('cible','le mot visé')} » (en {rl.get('latence_sec','?')} s).")
        else:
            bits.append(f"Le mot « {rl.get('cible','visé')} » n'est pas revenu aujourd'hui, sans détresse.")
    sig = rec.get("signal_famille", "vert")
    if sig == "vert":
        bits.append("Bonne humeur et engagement — rien à signaler.")
    elif sig == "orange":
        bits.append("Un peu de fatigue ou d'hésitation aujourd'hui — c'est un bon moment pour l'appeler.")
    else:
        bits.append("Signes de détresse pendant la séance — l'orthophoniste a été prévenu. Appelez-la dès que possible.")
    return " ".join(bits)


def render(records: list[dict]) -> str:
    if not records:
        return "<html><body><p>Aucune séance enregistrée.</p></body></html>"
    last = records[-1]
    sig = last.get("signal_famille", "vert")
    color = COLORS.get(sig, "#3ddc97")
    call = sig in ("orange", "rouge")
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cognitive Companion — Nouvelles de Geneviève</title>
<style>
 body{{margin:0;font-family:-apple-system,'Segoe UI',system-ui,sans-serif;background:#0f141b;color:#eef2f7;
   display:flex;min-height:100vh;align-items:center;justify-content:center;padding:24px;}}
 .card{{max-width:480px;width:100%;background:#161e27;border:1px solid #283442;border-radius:24px;
   padding:34px 30px;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.4);}}
 .dot{{width:110px;height:110px;border-radius:50%;margin:0 auto 18px;background:{color};
   box-shadow:0 0 50px {color}88;}}
 h1{{margin:0 0 4px;font-size:26px;}} .status{{font-size:20px;font-weight:700;color:{color};margin-bottom:16px;}}
 p{{font-size:17px;line-height:1.55;color:#cfd7e2;}}
 .call{{margin-top:18px;display:{'block' if call else 'none'};font-size:16px;font-weight:600;
   color:{color};border:1px solid {color}66;border-radius:12px;padding:12px;}}
 .date{{margin-top:18px;font-size:13px;color:#7e8a99;}}
</style></head><body><div class="card">
 <div class="dot"></div>
 <h1>Geneviève — ce soir</h1>
 <div class="status">{html.escape(LABEL[sig])}</div>
 <p>{html.escape(resume(last))}</p>
 <div class="call">📞 C'est un bon moment pour l'appeler.</div>
 <div class="date">Séance {html.escape(last.get('session_id',''))} · {html.escape(last.get('date',''))}</div>
</div></body></html>"""


def main(argv: list[str]) -> int:
    journal = "journal/sessions.jsonl"
    out = "rapports/famille.html"
    if "--journal" in argv:
        journal = argv[argv.index("--journal") + 1]
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    records = [r for r in load(journal) if r.get("patient_id") == "mme-durand"]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(render(records))
    sig = records[-1]["signal_famille"] if records else "—"
    print(f"→ {out} (signal: {sig})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
