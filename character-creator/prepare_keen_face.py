"""Register a face whose broad eyebrow is fused with the upper eye outline."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parent

def main():
 atlas=Image.open(ROOT/'sources/keen-expressions.png').convert('RGBA')
 for index,name in enumerate(['Face 01.png','Face 03.png','Face 02.png']):
  cell=atlas.crop((index*atlas.width//3,0,(index+1)*atlas.width//3,atlas.height));a=np.array(cell);a[:,:,3]=np.where(a[:,:,3]>160,255,0);cell=Image.fromarray(a);cell=cell.crop(cell.getchannel('A').getbbox()).resize((204,129),Image.Resampling.LANCZOS)
  out=Image.new('RGBA',(320,240));out.paste(cell,(60,53));d=np.array(out);r,g,b=d[:,:,:3].astype(float).transpose(2,0,1);opaque=d[:,:,3]>0
  # The colored brow occupies the broad dark upper-eye band itself. Erosion
  # leaves a charcoal rim; there is no detached eyebrow above the eye.
  dark=opaque&(np.maximum.reduce([r,g,b])<140);dark[125:,:]=False
  brows=distance_transform_edt(dark)>1.5
  eyes=opaque&(g>r*1.3)&(b>r*1.3)&(g>65)&~brows
  d[opaque&(np.maximum.reduce([r,g,b])<140),:3]=[27,26,24]
  for material,region,base in [('brows',brows,[64,57,47]),('eyes',eyes,[83,163,168])]:
   d[region,:3]=base;m=np.zeros_like(d);m[:,:,:3]=128;m[:,:,3]=np.where(region,d[:,:,3],0)
   dest=ROOT/'assets/masks/faces/keen'/(Path(name).stem+'-'+material+'.png');dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(m).save(dest)
  dest=ROOT/'assets/faces/keen'/name;dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(d).save(dest)
 print('Prepared Perspicaz: fused brow/upper-eye bands and three expressions.')
if __name__=='__main__':main()
