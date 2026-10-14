"""Build editable vector exports and a texture-animation Unity package.

Requires vtracer, Inkscape, Playwright, and the local HTTP preview server.
The SVG/EPS assets are vectorizations of the generated textures, not native AI.
"""
import io
import json
import math
import subprocess
import tarfile
import uuid
import os
import xml.etree.ElementTree as ET
from pathlib import Path
import vtracer
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CHARACTER = ROOT / 'characters/elf-mage'
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)

def idle_pose():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
        page=browser.new_page()
        page.goto('http://127.0.0.1:8765/characters/elf-mage/')
        page.wait_for_function('window.spriteReady')
        pose=page.evaluate('''async () => {
            const {SpriterPlayer}=await import('./player.js');
            const p=await new SpriterPlayer().load();
            const a=p.rig.animations.find(a=>a.name==='Idle'), m=a.mainline[0], bones={};
            for(const r of m.bones) bones[r.id]=p.world(p.sample(a,r,0),bones[r.parent]);
            return [...m.objects].sort((a,b)=>Number(a.z_index)-Number(b.z_index)).map(r=>({
                file:p.rig.files[p.sample(a,r,0).file],
                world:p.world(p.sample(a,r,0),bones[r.parent])}));
        }''')
        browser.close()
        return pose

def main():
    vectors = CHARACTER / 'AI' / 'Parts'
    eps = CHARACTER / 'EPS'
    unity = CHARACTER / 'Unity Package'
    for directory in [vectors, eps, unity]:
        directory.mkdir(parents=True, exist_ok=True)
    for texture in sorted((CHARACTER / 'PNG/Vector Parts').glob('*.png')):
        path = vectors / (texture.stem + '.svg')
        vtracer.convert_image_to_svg_py(str(texture), str(path), colormode='color',
                                      hierarchical='stacked', mode='spline',
                                      filter_speckle=3, color_precision=5,
                                      layer_difference=16, path_precision=3)
        subprocess.run(['inkscape', str(path), '--export-type=eps',
                        '--export-filename=' + str(eps / ('ElfMage_' + texture.stem + '.eps'))],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    assembled = ET.Element('{' + SVG + '}svg', {'width':'900','height':'900','viewBox':'0 0 900 900'})
    # Bake the Idle world transforms into separate named, editable layers.
    for item in idle_pose():
        file, transform = item['file'], item['world']
        if float(transform.get('a', 1)) == 0:
            continue
        width, height = int(file['width']), int(file['height'])
        pivot_x = float(transform.get('pivot_x',file.get('pivot_x',0)))
        pivot_y = float(transform.get('pivot_y',file.get('pivot_y',1)))
        x, y = float(transform['x'])+450, 750-float(transform['y'])
        rotation = -float(transform['angle'])
        sx, sy = float(transform.get('scale_x',1)), float(transform.get('scale_y',1))
        layer = ET.SubElement(assembled, '{' + SVG + '}g', {
            'id':Path(file['name']).stem.replace(' ','_'),
            'transform':f'translate({x} {y}) rotate({rotation}) scale({sx} {sy}) translate({-pivot_x*width} {-(1-pivot_y)*height})'})
        vector = ET.parse(vectors / (Path(file['name']).stem + '.svg')).getroot()
        for child in vector:
            layer.append(child)
    source = CHARACTER / 'AI/ElfMage.svg'
    ET.ElementTree(assembled).write(source, encoding='utf-8', xml_declaration=True)
    subprocess.run(['inkscape',str(source),'--export-type=pdf',
                    '--export-filename='+str(CHARACTER/'AI/ElfMage.pdf')],
                   check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

    # Unity's .unitypackage is a gzip tar with per-asset GUID directories.
    assets = []
    for texture in sorted((CHARACTER/'PNG').rglob('*.png')):
        relative=texture.relative_to(CHARACTER/'PNG')
        if relative.parts[0]=='PNG Sequences':
            path='Assets/ElfMage/Resources/ElfMage/' + relative.as_posix()
        else:
            path='Assets/ElfMage/PNG/' + relative.as_posix()
        assets.append((path,texture.read_bytes(),'texture'))
    assets.append(('Assets/ElfMage/PNG/Vector Parts/Animations.scml',
                   (CHARACTER/'PNG/Vector Parts/Animations.scml').read_bytes(),'other'))
    assets.append(('Assets/ElfMage/ElfMageAnimator.cs',
                   (unity/'ElfMageAnimator.cs').read_bytes(),'script'))
    assets.append(('Assets/ElfMage/README.txt',(unity/'README.txt').read_bytes(),'other'))
    with tarfile.open(unity/'ElfMage.unitypackage','w:gz') as package:
        for path, data, kind in assets:
            guid=uuid.uuid5(uuid.NAMESPACE_URL,'fighthub2026-cloud/sprites/'+path).hex
            if kind=='texture':
                meta=f'''fileFormatVersion: 2
guid: {guid}
TextureImporter:
  serializedVersion: 12
  mipmaps:
    enableMipMap: 0
  isReadable: 0
  textureType: 8
  spriteMode: 1
  spritePixelsToUnits: 100
  spritePivot: {{x: 0.5, y: 0.1666667}}
  alphaIsTransparency: 1
  maxTextureSize: 2048
  textureCompression: 0
  filterMode: 1
  wrapMode: 1
'''
            elif kind=='script':
                meta=f'fileFormatVersion: 2\nguid: {guid}\nMonoImporter:\n  externalObjects: {{}}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n'
            else:
                meta=f'fileFormatVersion: 2\nguid: {guid}\nDefaultImporter:\n  externalObjects: {{}}\n'
            for name, contents in [('asset',data),('asset.meta',meta.encode()),('pathname',path.encode())]:
                info=tarfile.TarInfo(guid+'/'+name)
                info.size=len(contents)
                package.addfile(info,io.BytesIO(contents))
    print(f'Built 13 SVG/EPS parts, layered SVG/PDF and Unity package with {len(assets)} assets.')

if __name__ == '__main__':
    main()
