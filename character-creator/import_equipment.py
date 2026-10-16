"""Import the native Craftpix PNGs without resampling their original artwork."""
import argparse
import io
import json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('staves', type=Path)
    parser.add_argument('shields', type=Path)
    args = parser.parse_args()
    catalog = {}
    for kind, archive, prefix, title, size in [
        ('staves', args.staves, 'Staves', 'Cajado', (400, 128)),
        ('shields', args.shields, 'Shield', 'Escudo', (160, 160)),
    ]:
        entries = []
        with ZipFile(archive) as source:
            for model in range(1, 9):
                for variant in range(1, 6):
                    original = f'PNG/{prefix}_{model}/{variant}.png'
                    content = source.read(original)
                    with Image.open(io.BytesIO(content)) as image:
                        assert image.size == size and image.mode == 'RGBA', original
                    key = f'accessories/{kind}/{model}-{variant}.png'
                    dest = ROOT / 'assets' / key
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(content)
                    entries.append({'name': f'{title} {model} · variante {variant}',
                                    'key': key, 'source': original})
        catalog[kind] = entries
    (ROOT / 'equipment.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    print('Imported 40 native staves and 40 native shields.')

if __name__ == '__main__':
    main()
