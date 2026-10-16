"""Prepare every piece of Vector Parts (2), using the established pack rules."""
from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import label,find_objects
import json
from prepare_fallen import material_masks,INK
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'assets/imported/vector-parts-2'
SKIN=np.array([[211,188,180],[158,141,135],[180,160,153]],float)
HOOD=np.array([[81,70,70],[61,52,52],[109,94,94],[46,39,39],[61,48,48]],float)
OTHER=np.array([[234,226,223],[175,169,167],[255,240,235]],float)

def main():
 dest=ROOT/'assets/packs/spectral';dest.mkdir(parents=True,exist_ok=True)
 for source in SOURCE.glob('*.png'):
  d=np.array(Image.open(source).convert('RGBA'));rgb=d[:,:,:3].astype(int);ink=(rgb.max(2)<=42)&((rgb.max(2)-rgb.min(2))<=14)&(d[:,:,3]>0);d[ink,:3]=INK.astype('uint8');Image.fromarray(d).save(dest/source.name)
 material_masks(dest/'Head.png',[('skin',SKIN,[128,96,108]),('hair',HOOD,[128,96,150,74,88])])
 for name in ['Right Hand.png','Left Hand.png']:
  material_masks(dest/name,[('skin',SKIN,[128,96,108]),(None,HOOD,[128]*len(HOOD)),(None,OTHER,[128]*len(OTHER))])
 faces=ROOT/'assets/faces/spectral';faces.mkdir(parents=True,exist_ok=True)
 for name in ['Face 01.png','Face 02.png','Face 03.png']:
  d=np.array(Image.open(SOURCE/name).convert('RGBA'));r,g,b=d[:,:,:3].astype(float).transpose(2,0,1);opaque=d[:,:,3]>0
  # Source eyebrow fills are neutral grey, isolated from white sclera by ink.
  neutral=opaque&(r>60)&(abs(r-g)<25)&(abs(g-b)<22)
  components,_=label(neutral);brows=np.zeros_like(opaque)
  for i,box in enumerate(find_objects(components)):
   if box is not None and box[0].start<90 and np.count_nonzero(components[box]==i+1)>30:brows|=components==i+1
  eyes=opaque&(b>r*1.2)&(g>r*1.08)&(b>g*1.04)&(b>65)&~brows
  d[opaque&(np.maximum.reduce([r,g,b])<65),:3]=INK.astype('uint8')
  lum=r*.2126+g*.7152+b*.0722;shades=np.where(lum<140,96,np.where(lum>205,210,128))
  if name!='Face 01.png':
   d[brows,:3]=INK.astype('uint8');brows[:]=False
  for material,region,base in [('brows',brows,np.array([175,169,167])),('eyes',eyes,np.array([146,190,217]))]:
   shade=shades if material=='brows' else np.full_like(shades,128)
   colors=np.where((shade<=128)[:,:,None],base*shade[:,:,None]/128,base+(255-base)*(shade[:,:,None]-128)/127)
   d[region,:3]=np.clip(colors[region],0,255).astype('uint8');m=np.zeros_like(d);m[:,:,:3]=shade[:,:,None];m[:,:,3]=np.where(region,d[:,:,3],0)
   path=ROOT/'assets/masks/faces/spectral'/(Path(name).stem+'-'+material+'.png');path.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(m).save(path)
  Image.fromarray(d).save(faces/name)
 config=json.loads((ROOT/'head-registration.json').read_text());config['styles']['spectral']={'scaleX':1,'offsetX':0,'scaleY':1,'offsetY':0};(ROOT/'head-registration.json').write_text(json.dumps(config,indent=2)+'\n')
 print('Prepared Espectral: all 13 parts, 3 native expressions and recolor masks.')
if __name__=='__main__':main()
