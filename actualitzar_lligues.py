#!/usr/bin/env python3
"""
actualitzar_lligues.py
Genera lligues_europees.html amb les classificacions actuals
de les 7 principals lligues europees via API football-data.org

Ús: python3 actualitzar_lligues.py
Requereix: pip install requests
API key gratuïta: https://www.football-data.org/client/register
"""

import requests
import json
import os
from datetime import datetime

# ─── CONFIGURACIÓ ────────────────────────────────────────────────────────────
API_KEY = os.getenv("FOOTBALL_API_KEY", "")  # Posa la teva clau aquí o en variable d'entorn
BASE_URL = "https://api.football-data.org/v4"
HEADERS  = {"X-Auth-Token": API_KEY}

LLIGUES = [
    {"codi": "PD",  "nom": "LaLiga EA Sports",       "pais": "🇪🇸", "color": "#c60b1e"},
    {"codi": "PL",  "nom": "Premier League",          "pais": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "color": "#3d195b"},
    {"codi": "BL1", "nom": "Bundesliga",              "pais": "🇩🇪", "color": "#d30010"},
    {"codi": "SA",  "nom": "Serie A",                 "pais": "🇮🇹", "color": "#009225"},
    {"codi": "FL1", "nom": "Ligue 1 McDonald's",      "pais": "🇫🇷", "color": "#002056"},
    {"codi": "PPL", "nom": "Liga Portugal Betclic",   "pais": "🇵🇹", "color": "#006129"},
    {"codi": "DED", "nom": "Eredivisie",              "pais": "🇳🇱", "color": "#AE1635"},
]

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lligues_europees.html")


def get_standings(codi):
    """Obté la classificació d'una lliga."""
    url = f"{BASE_URL}/competitions/{codi}/standings"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        data = r.json()
        # Agafa el total standings (no per casa/fora)
        for t in data.get("standings", []):
            if t.get("type") == "TOTAL":
                return t.get("table", [])[:10]  # Top 10
    elif r.status_code == 429:
        print(f"  Rate limit hit per {codi}. Espera i torna a provar.")
    else:
        print(f"  Error {r.status_code} per {codi}")
    return []


def build_card(lliga, taula):
    """Genera el HTML d'una targeta de lliga."""
    color = lliga["color"]
    files = ""
    for i, equip in enumerate(taula, 1):
        nom = equip.get("team", {}).get("name", "—")
        pj  = equip.get("playedGames", "—")
        pts = equip.get("points", "—")
        pos = equip.get("position", i)
        cls = ""
        if pos <= 4:   cls = "ucl"
        elif pos == 5: cls = "uel"
        elif pos == 6: cls = "uecl"
        elif pos >= 17: cls = "rel"
        first = " champion-row" if pos == 1 else ""
        files += f'<tr class="{cls}{first}"><td class="pos">{pos}</td>'
        files += f'<td class="team-name">{nom}</td><td>{pj}</td>'
        files += f'<td class="pts">{pts}</td></tr>\n'

    return f"""
  <div class="card">
    <div class="card-header" style="background: linear-gradient(135deg, {color}22, {color}11);">
      <span class="flag">{lliga["pais"]}</span>
      <span>{lliga["nom"]}</span>
    </div>
    <table>
      <thead><tr><th>#</th><th>Equip</th><th>PJ</th><th>Pts</th></tr></thead>
      <tbody>
{files}      </tbody>
    </table>
    <div class="legend">
      <div class="leg-item"><div class="leg-dot leg-ucl"></div>Champions</div>
      <div class="leg-item"><div class="leg-dot leg-uel"></div>Europa</div>
      <div class="leg-item"><div class="leg-dot leg-uecl"></div>Conference</div>
      <div class="leg-item"><div class="leg-dot leg-rel"></div>Descens</div>
    </div>
  </div>"""


CSS = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #0f1117; color: #e8e8e8; padding: 20px; }
    h1 { text-align: center; font-size: 1.8rem; color: #fff; margin-bottom: 6px; }
    .subtitle { text-align: center; color: #888; font-size: 0.85rem; margin-bottom: 28px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; max-width: 1400px; margin: 0 auto; }
    .card { background: #1a1d27; border-radius: 12px; overflow: hidden; border: 1px solid #2a2d3a; }
    .card-header { display: flex; align-items: center; gap: 12px; padding: 14px 16px; font-weight: 700; font-size: 1rem; }
    .flag { font-size: 1.5rem; }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; padding: 7px 10px; font-size: 0.7rem; color: #666; text-transform: uppercase; background: #13151e; border-bottom: 1px solid #2a2d3a; }
    td { padding: 9px 10px; font-size: 0.875rem; border-bottom: 1px solid #1e2130; }
    tr:last-child td { border-bottom: none; }
    .pos { color: #666; font-size: 0.8rem; }
    .team-name { font-weight: 600; }
    .pts { font-weight: 700; color: #fff !important; }
    .champion-row .team-name, .champion-row .pts { color: #ffd700 !important; }
    .ucl { border-left: 3px solid #1a73e8; }
    .uel { border-left: 3px solid #f57c00; }
    .uecl { border-left: 3px solid #2e7d32; }
    .rel { border-left: 3px solid #c62828; }
    .legend { display: flex; gap: 16px; padding: 10px 16px; background: #13151e; border-top: 1px solid #2a2d3a; flex-wrap: wrap; }
    .leg-item { display: flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #888; }
    .leg-dot { width: 10px; height: 14px; border-radius: 2px; }
    .leg-ucl { background: #1a73e8; } .leg-uel { background: #f57c00; }
    .leg-uecl { background: #2e7d32; } .leg-rel { background: #c62828; }
    .updated { text-align: center; color: #555; font-size: 0.75rem; margin-top: 24px; }
"""


def main():
    if not API_KEY:
        print("⚠️  Cal definir FOOTBALL_API_KEY.")
        print("   Obté una clau gratuïta a https://www.football-data.org/client/register")
        return

    print(f"Actualitzant lligues — {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    cards_html = ""
    for lliga in LLIGUES:
        print(f"  Obtenint {lliga['nom']}...")
        taula = get_standings(lliga["codi"])
        if taula:
            cards_html += build_card(lliga, taula)
        else:
            print(f"  ⚠️  No s'han pogut obtenir dades per {lliga['nom']}")
        # Pausa per respectar el rate limit (1 req/s pla gratuït)
        import time; time.sleep(6)

    ara = datetime.now().strftime("%d/%m/%Y %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="ca">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lligues Europees 2025/26</title>
  <style>{CSS}</style>
</head>
<body>
<h1>⚽ Lligues Europees 2025/26</h1>
<p class="subtitle">Actualitzat: {ara}</p>
<div class="grid">
{cards_html}
</div>
<p class="updated">Font: football-data.org · Actualitzat automàticament</p>
</body>
</html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Fitxer generat: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
