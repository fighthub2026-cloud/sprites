"""Register a face whose broad eyebrow is fused with the upper eye outline."""
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def main():
 atlas=Image.open(ROOT/'sources/keen-expressions.png').convert('RGBA')
 for index,name in enumerate(['Face 01.png','Face 03.png','Face 02.png']):
  cell=atlas.crop((index*atlas.width//3,0,(index+1)*atlas.width//3,atlas.height));a=np.array(cell);a[:,:,3]=np.where(a[:,:,3]>160,255,0);cell=Image.fromarray(a);cell=cell.crop(cell.getchannel('A').getbbox()).resize((204,129),Image.Resampling.LANCZOS)
  out=Image.new('RGBA',(320,240));out.paste(cell,(60,53));d=np.array(out);r,g,b=d[:,:,:3].astype(float).transpose(2,0,1);opaque=d[:,:,3]>0
  # The atlas explicitly paints the eyebrow interior green. Segment that
  # material only: never infer an eyebrow from the dark eye contour.
  brows=opaque&(g>r*1.22)&(g>b*1.12)&(g>75)
  eyes=opaque&(g>r*1.2)&(b>r*1.25)&(b>=g*.95)&(g>65)&~brows
  # Every uncolored dark outline remains charcoal, including the divider
  # between the eyebrow fill and the eye's white sclera.
  d[opaque&(np.maximum.reduce([r,g,b])<65),:3]=[27,26,24]
  for material,region,base in [('brows',brows,[78,174,135]),('eyes',eyes,[83,163,168])]:
   d[region,:3]=base;m=np.zeros_like(d);m[:,:,:3]=128;m[:,:,3]=np.where(region,d[:,:,3],0)
   dest=ROOT/'assets/masks/faces/keen'/(Path(name).stem+'-'+material+'.png');dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(m).save(dest)
  dest=ROOT/'assets/faces/keen'/name;dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(d).save(dest)
 print('Prepared Perspicaz: fused brow/upper-eye bands and three expressions.')
if __name__=='__main__':main()
