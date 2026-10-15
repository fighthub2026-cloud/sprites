"""Build an offline, single-file character creator from its local sources."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent

def main():
    player=(ROOT.parent/'characters/goblin/player.js').read_text().replace('export class SpriterPlayer','class SpriterPlayer')
    html=(ROOT/'template.html').read_text().replace('/*STYLE*/',(ROOT/'style.css').read_text()).replace('/*CATALOG*/',(ROOT/'catalog.json').read_text()).replace('/*PLAYER*/',player).replace('/*APP*/',(ROOT/'app.js').read_text())
    (ROOT/'index.html').write_text(html)
    print(f'Built {ROOT / "index.html"}: {len(html.encode())} bytes')

if __name__=='__main__':main()
