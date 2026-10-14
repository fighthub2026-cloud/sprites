"""Pack generated texture atlases into the dimensions of the Spriter rig.

This only crops atlas cells, resizes, and registers their transparent bounds.
ImageMagick supplies the PNG export; Pillow reads alpha bounds.
"""
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'characters/elf-mage/PNG/Vector Parts'
SOURCE = ROOT / 'characters/elf-mage/Sources'

def pack(name, source, size, target, cell=None):
    image = Image.open(SOURCE / source)
    if cell:
        image = image.crop(cell)
    bounds = image.getchannel('A').point(lambda a: 255 if a > 128 else 0).getbbox()
    if not bounds:
        raise ValueError(f'Empty texture: {name}')
    left, top, right, bottom = bounds
    if cell:
        left += cell[0]; right += cell[0]
        top += cell[1]; bottom += cell[1]
    x, y, width, height = target
    subprocess.run(['convert', str(SOURCE / source), '-crop', f'{right-left}x{bottom-top}+{left}+{top}',
                    '+repage', '-resize', f'{width}x{height}!',
                    '-background', 'none', '-gravity', 'NorthWest',
                    '-extent', f'{size[0]}x{size[1]}-{x}-{y}', str(OUTPUT / name)], check=True)

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    pack('Head.png', 'head.png', (480,480), (35,5,410,442))
    pack('Body.png', 'body.png', (320,320), (58,62,205,214))
    names = ['Right Arm.png','Right Hand.png','Right Leg.png','Left Arm.png','Left Hand.png','Left Leg.png']
    targets = [(19,20,79,94),(24,22,81,84),(24,23,80,82),(30,24,77,87),(28,30,73,69),(26,25,77,78)]
    width,height = Image.open(SOURCE / 'limbs.png').size
    for i,(name,target) in enumerate(zip(names,targets)):
        col,row = i%3,i//3
        cell = (col*width//3,row*height//2,(col+1)*width//3,(row+1)*height//2)
        pack(name,'limbs.png',(128,128),target,cell)
    width,height = Image.open(SOURCE / 'faces.png').size
    # Expressions share the same source registration; do not independently
    # stretch closed eyes to the height of the open-eye expression.
    atlas=Image.open(SOURCE / 'faces.png')
    bounds=[atlas.crop((i*width//3,0,(i+1)*width//3,height)).getchannel('A').point(lambda a:255 if a>128 else 0).getbbox() for i in range(3)]
    l=min(b[0] for b in bounds);t=min(b[1] for b in bounds)
    r=max(b[2] for b in bounds);b=max(b[3] for b in bounds)
    for i in range(3):
        subprocess.run(['convert',str(SOURCE/'faces.png'),'-crop',f'{r-l}x{b-t}+{i*width//3+l}+{t}',
                        '+repage','-resize','185x155!','-background','none','-gravity','NorthWest',
                        '-extent','320x240-68-45',str(OUTPUT/f'Face 0{i+1}.png')],check=True)
    pack('Staff.png','staff.png',(400,128),(65,0,325,128))
    pack('SlashFX.png','effect.png',(496,496),(39,12,418,472))

if __name__ == '__main__':
    main()
