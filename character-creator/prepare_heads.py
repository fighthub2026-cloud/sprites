"""Extract hair materials as overlays without retaining their old face contours."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import binary_closing,binary_opening,distance_transform_edt,label
ROOT=Path(__file__).resolve().parent

def main():
 for name in ['short','silver','blue','blond']:
  old=np.array(Image.open(ROOT/'assets/masks/heads'/f'{name}-hair.png').convert('RGBA'))
  fill=binary_closing(binary_opening(old[:,:,3]>0,iterations=1),iterations=2)
  components,_=label(fill);sizes=np.bincount(components.ravel());sizes[0]=0;fill=sizes[components]>200
  # Rebuild a continuous ink border from the hair silhouette. Reusing nearby
  # source ink also imports fragments of each different ear and cheek outline.
  distance,nearest=distance_transform_edt(~fill,return_indices=True)
  outline=distance<=7
  shades=old[:,:,0][nearest[0],nearest[1]]
  shades=np.where(np.isin(shades,[100,128,150]),shades,128)
  d=np.zeros((480,480,4),dtype='uint8');d[outline]=[27,26,24,255]
  colors={'short':[60,61,64],'silver':[208,210,215],'blue':[125,175,226],'blond':[250,197,79]}
  base=np.array(colors[name]);rgb=np.where((shades<=128)[:,:,None],base*shades[:,:,None]/128,base+(255-base)*(shades[:,:,None]-128)/127)
  d[fill,:3]=np.clip(rgb[fill],0,255).astype('uint8')
  dest=ROOT/'assets/hair'/f'{name}.png';dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(d).save(dest)
  # Keep common skin below the hairline, never behind gaps between tufts.
  base_mask=np.zeros_like(d)
  for x in range(480):
   ys=np.flatnonzero(outline[:300,x]);start=max(150,int(ys[-1])+1 if len(ys) else 300)
   base_mask[start:,x]=[255,255,255,255]
  Image.fromarray(base_mask).save(ROOT/'assets/hair'/f'{name}-base-mask.png')
  mask=np.zeros_like(d);mask[:,:,:3]=shades[:,:,None];mask[:,:,3]=np.where(fill,255,0)
  dest=ROOT/'assets/masks/hair'/f'{name}-hair.png';dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(mask).save(dest)
 print('Prepared 4 isolated hair overlays for one shared head base.')
if __name__=='__main__':main()
