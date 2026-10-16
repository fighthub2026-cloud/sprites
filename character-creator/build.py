"""Build an offline, single-file character creator from its local sources."""
from pathlib import Path
import json
import base64
ROOT=Path(__file__).resolve().parent

def main():
    images={p.relative_to(ROOT/'assets').as_posix():'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode() for p in (ROOT/'assets').rglob('*.png')}
    catalog={'images':images,'equipment':json.loads((ROOT/'equipment.json').read_text()),'shieldRig':json.loads((ROOT/'shield-rig.json').read_text()),'shieldSCML':(ROOT/'shield.scml').read_text(),'guardianSCML':(ROOT/'assets/imported/guardian/Animations.scml').read_text(),'guardianViewsSCML':(ROOT/'assets/imported/guardian/Animations.autosave.scml').read_text(),'headRegistration':json.loads((ROOT/'head-registration.json').read_text()),'rig':json.loads((ROOT/'rig.json').read_text()),'scml':(ROOT/'assets/original/Animations.scml').read_text()}
    (ROOT/'catalog.json').write_text(json.dumps(catalog,separators=(',',':')))
    player=(ROOT.parent/'characters/goblin/player.js').read_text().replace('export class SpriterPlayer','class SpriterPlayer')
    html=(ROOT/'template.html').read_text().replace('/*STYLE*/',(ROOT/'style.css').read_text()).replace('/*CATALOG*/',(ROOT/'catalog.json').read_text()).replace('/*PLAYER*/',player).replace('/*APP*/',(ROOT/'app.js').read_text())
    (ROOT/'index.html').write_text(html)
    print(f'Built {ROOT / "index.html"}: {len(html.encode())} bytes')

if __name__=='__main__':main()
