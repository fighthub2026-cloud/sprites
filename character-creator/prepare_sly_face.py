"""Register the sly face atlas without changing the other catalog entries."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import label,find_objects,distance_transform_edt
ROOT=Path(__file__).resolve().parent

def main():
 atlas=Image.open(ROOT/'sources/sly-expressions.png').convert('RGBA')
 for index,name in enumerate(['Face 01.png','Face 03.png','Face 02.png']):
  cell=atlas.crop((index*atlas.width//3,0,(index+1)*atlas.width//3,atlas.height));raw=np.array(cell);raw[:,:,3]=np.where(raw[:,:,3]>160,255,0);cell=Image.fromarray(raw);cell=cell.crop(cell.getchannel('A').getbbox()).resize((204,129),Image.Resampling.LANCZOS)
  out=Image.new('RGBA',(320,240));out.paste(cell,(60,53));d=np.array(out);r,g,b=d[:,:,:3].astype(float).transpose(2,0,1);opaque=d[:,:,3]>0
  components,_=label(d[:,:,3]>160);brows=np.zeros_like(opaque)
  for i,sl in enumerate(find_objects(components)):
   if sl and sl[0].start<75 and sl[0].stop<115:
    region=components==i+1;brows|=distance_transform_edt(region)>1.2
  eyes=opaque&(g>r*1.3)&(b>r*1.3)&(g>65)&~brows
  d[opaque&(np.maximum.reduce([r,g,b])<65),:3]=[27,26,24]
  for material,region,base in [('brows',brows,[70,60,52]),('eyes',eyes,[83,163,168])]:
   d[region,:3]=base
   m=np.zeros_like(d);m[:,:,:3]=128;m[:,:,3]=np.where(region,d[:,:,3],0)
   dest=ROOT/'assets/masks/faces/sly'/(Path(name).stem+'-'+material+'.png');dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(m).save(dest)
  # Add a two-pixel charcoal stroke beneath the original drawing.
  original=Image.fromarray(d);stroke=Image.new('RGBA',original.size,(27,26,24,0));stroke.putalpha(original.getchannel('A').filter(ImageFilter.MaxFilter(5)));stroke.alpha_composite(original)
  dest=ROOT/'assets/faces/sly'/name;dest.parent.mkdir(parents=True,exist_ok=True);stroke.save(dest)
 print('Prepared Astuto: open, blink and hurt, with independent color masks.')
if __name__=='__main__':main()
