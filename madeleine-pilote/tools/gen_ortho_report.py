#!/usr/bin/env python3
"""
gen_ortho_report.py — Agrège les séances de la semaine en un RAPPORT ORTHOPHONISTE
(rapports/ortho-hebdo.html) qui fait apparaître une COURBE d'évolution sur ≥ 1
métrique (latence d'accès lexical ↓ et durée d'engagement ↑), plus un tableau :
catégories de mots tentées, exactitude du rappel, durée d'engagement, drapeaux.

Lisible en 5 min (l'ortho est en surcharge — argument d'adoption, DD). Courbes en
SVG inline, aucune dépendance. Layer 3, déterministe.

Usage : python3 tools/gen_ortho_report.py [--journal ...] [--out rapports/ortho-hebdo.html]
"""
from __future__ import annotations
import sys, json, os, html


def load(journal: str) -> list[dict]:
    if not os.path.exists(journal):
        return []
    return [json.loads(l) for l in open(journal, encoding="utf-8") if l.strip()]


def sparkline(values, w=520, h=140, pad=28, color="#60a5fa", lower_is_better=False):
    """Petite courbe SVG. Retourne le markup. Points = valeurs dans l'ordre."""
    vals = [v for v in values if isinstance(v, (int, float))]
    if len(vals) < 2:
        return f'<svg width="{w}" height="{h}"><text x="10" y="20" fill="#7e8a99" font-size="12">Pas assez de points</text></svg>'
    vmin, vmax = min(vals), max(vals)
    span = (vmax - vmin) or 1
    n = len(vals)
    def x(i): return pad + i * (w - 2 * pad) / (n - 1)
    def y(v): return h - pad - (v - vmin) / span * (h - 2 * pad)
    pts = [(x(i), y(v)) for i, v in enumerate(vals)]
    poly = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    dots = "".join(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color}"/>' for px, py in pts)
    area = f"{pad},{h-pad} " + poly + f" {w-pad},{h-pad}"
    # flèche de tendance
    improving = (vals[-1] < vals[0]) if lower_is_better else (vals[-1] > vals[0])
    trend = "▼ amélioration" if improving else "△ à surveiller"
    tcol = "#3ddc97" if improving else "#f5b14c"
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
      <polygon points="{area}" fill="{color}14"/>
      <polyline points="{poly}" fill="none" stroke="{color}" stroke-width="2.5"/>
      {dots}
      <text x="{pad}" y="16" fill="{tcol}" font-size="12" font-weight="700">{trend}</text>
      <text x="{w-pad}" y="{h-6}" fill="#7e8a99" font-size="11" text-anchor="end">{vals[0]} → {vals[-1]}</text>
    </svg>'''


def render(records: list[dict]) -> str:
    recs = sorted(records, key=lambda r: r.get("date", ""))
    dates = [r.get("date", "") for r in recs]
    latence = [r.get("rappel_lexical", {}).get("latence_sec") for r in recs]
    engage = [round(r.get("duree_engagement_sec", 0) / 60, 1) for r in recs]
    wpm = [r.get("fluence", {}).get("mots_par_minute") for r in recs]

    rows = ""
    for r in recs:
        rl = r.get("rappel_lexical", {})
        seq = r.get("sequencage", {})
        eng = r.get("engagement", {})
        sig = r.get("signal_famille", "—")
        sigcol = {"vert": "#3ddc97", "orange": "#f5b14c", "rouge": "#ef5a5a"}.get(sig, "#7e8a99")
        rows += f"""<tr>
          <td>{html.escape(r.get('date',''))}<br><span class="muted">{html.escape(r.get('session_id',''))}</span></td>
          <td>{html.escape(r.get('exercice',''))}</td>
          <td>{'✓' if rl.get('exact') else '—'} <span class="muted">{rl.get('latence_sec','?')} s · {rl.get('paraphasies','?')} paraph.</span></td>
          <td>{seq.get('etapes_correctes','?')}/{seq.get('etapes_total','?')}</td>
          <td>{round(r.get('duree_engagement_sec',0)/60,1)} min</td>
          <td>{html.escape(str(eng.get('maintien_sujet','—')))}</td>
          <td><span style="color:{sigcol};font-weight:700">●</span> {html.escape(', '.join(r.get('drapeaux',[])) or '—')}</td>
        </tr>"""

    n = len(recs)
    period = f"{dates[0]} → {dates[-1]}" if recs else "—"
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Madeleine — Rapport orthophoniste · Mme Durand</title>
<style>
 body{{margin:0;font-family:-apple-system,'Segoe UI',system-ui,sans-serif;background:#0f141b;color:#eef2f7;padding:28px;}}
 .wrap{{max-width:820px;margin:0 auto;}}
 h1{{font-size:24px;margin:0 0 2px;}} .sub{{color:#9aa6b6;font-size:14px;margin-bottom:22px;}}
 .grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:22px;}}
 .panel{{background:#161e27;border:1px solid #283442;border-radius:16px;padding:16px;}}
 .panel h3{{margin:0 0 2px;font-size:13px;color:#cfd7e2;}} .panel .cap{{font-size:11px;color:#7e8a99;margin-bottom:8px;}}
 table{{width:100%;border-collapse:collapse;background:#161e27;border:1px solid #283442;border-radius:16px;overflow:hidden;}}
 th,td{{text-align:left;padding:10px 12px;font-size:13px;border-bottom:1px solid #222c38;vertical-align:top;}}
 th{{background:#1b2430;color:#9aa6b6;font-size:11px;text-transform:uppercase;letter-spacing:.06em;}}
 .muted{{color:#7e8a99;font-size:11px;}}
 .kpis{{display:flex;gap:14px;margin-bottom:22px;flex-wrap:wrap;}}
 .kpi{{background:#161e27;border:1px solid #283442;border-radius:14px;padding:12px 16px;min-width:120px;}}
 .kpi .v{{font-size:22px;font-weight:700;}} .kpi .l{{font-size:11px;color:#7e8a99;}}
 .foot{{margin-top:18px;font-size:11px;color:#6b7686;line-height:1.5;}}
</style></head><body><div class="wrap">
 <h1>Rapport orthophoniste — Mme Geneviève Durand</h1>
 <div class="sub">Période {html.escape(period)} · {n} séance(s) · stimulation conversationnelle (SRT / SFA / réminiscence) · lecture ≈ 5 min</div>

 <div class="kpis">
   <div class="kpi"><div class="v">{n}</div><div class="l">séances</div></div>
   <div class="kpi"><div class="v">{(latence[0] if latence and latence[0] else '?')}→{(latence[-1] if latence and latence[-1] else '?')} s</div><div class="l">latence d'accès lexical</div></div>
   <div class="kpi"><div class="v">{engage[0]}→{engage[-1]} min</div><div class="l">durée d'engagement</div></div>
   <div class="kpi"><div class="v">{sum(1 for r in recs if r.get('rappel_lexical',{}).get('exact'))}/{n}</div><div class="l">rappels exacts</div></div>
 </div>

 <div class="grid">
   <div class="panel"><h3>Latence d'accès lexical (s)</h3><div class="cap">Plus bas = mot retrouvé plus vite ↓</div>{sparkline(latence, color='#60a5fa', lower_is_better=True)}</div>
   <div class="panel"><h3>Durée d'engagement (min)</h3><div class="cap">Plus haut = séance mieux tenue ↑</div>{sparkline(engage, color='#3ddc97')}</div>
 </div>

 <table>
   <tr><th>Date</th><th>Exercice</th><th>Rappel lexical</th><th>Séquençage</th><th>Engagement</th><th>Maintien sujet</th><th>Signal / drapeaux</th></tr>
   {rows}
 </table>

 <div class="foot">
   Catégories de mots tentées : prénoms des proches (SRT/EL), descriptions d'objets (SFA), thèmes de réminiscence (jardin, pâtisserie).
   Métriques objectives (durée, fluence) calculées automatiquement ; latence/paraphasies/maintien annotés sur le transcript.
   <b>Proto supervisé — non diagnostique.</b> Aucun entraînement cognitif décontextualisé (NICE NG97).
 </div>
</div></body></html>"""


def main(argv: list[str]) -> int:
    journal = "journal/sessions.jsonl"
    out = "rapports/ortho-hebdo.html"
    if "--journal" in argv:
        journal = argv[argv.index("--journal") + 1]
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    records = [r for r in load(journal) if r.get("patient_id") == "mme-durand"]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(render(records))
    print(f"→ {out} ({len(records)} séance(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
