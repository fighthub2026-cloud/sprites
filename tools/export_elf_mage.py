"""Export the assembled Spriter rig through its browser renderer.

Run a local HTTP server at repository root first:
  python -m http.server 8765 --bind 127.0.0.1
Then: python tools/export_elf_mage.py
Requires playwright and a Chromium installation (CHROMIUM_PATH overrides).
"""
import base64
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CHARACTER = ROOT / 'characters' / 'elf-mage'

def main():
    rig = json.loads((CHARACTER / 'rig.json').read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:8765/characters/elf-mage/')
        page.wait_for_function('window.spriteReady === true')
        frames = 0
        for animation in rig['animations']:
            name = animation['name']
            if name == 'Base':
                continue
            count = rig['frameCounts'][name]
            output = CHARACTER / 'PNG' / 'PNG Sequences' / name
            output.mkdir(parents=True, exist_ok=True)
            for index in range(count):
                milliseconds = index * float(animation['length']) / count
                data = page.evaluate('([name,t]) => window.renderFrame(name,t)', [name, milliseconds])
                (output / f'0_ElfMage_{name}_{index:03}.png').write_bytes(base64.b64decode(data.split(',', 1)[1]))
                frames += 1
        if errors:
            raise RuntimeError(errors)
        browser.close()
    idle = CHARACTER / 'PNG' / 'PNG Sequences' / 'Idle' / '0_ElfMage_Idle_000.png'
    (CHARACTER / 'idle.png').write_bytes(idle.read_bytes())
    print(f'Exported {frames} PNG frames across {len(rig["frameCounts"])} animations.')

if __name__ == '__main__':
    main()
