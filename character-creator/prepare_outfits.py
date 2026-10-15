"""Register the three garment designs to the existing torso and arm pivots."""
from pathlib import Path
from PIL import Image
import numpy as np
from prepare_native import outline
ROOT=Path(__file__).resolve().parent
def main():
 im=Image.open(ROOT/'sources/outfit-options.png').convert('RGBA')
 for i,kind in enumerate(['leather','vest','plate']):
  cell=im.crop((i*im.width//3,0,(i+1)*im.width//3,im.height));box=cell.getchannel('A').point(lambda a:255 if a>128 else 0).getbbox();body=cell.crop(box).resize((190,213),Image.Resampling.LANCZOS)
  out=Image.new('RGBA',(320,320));out.paste(body,(65,53));dest=ROOT/'assets/outfits'/kind;dest.mkdir(exist_ok=True,parents=True);outline(out).save(dest/'Body.png')
  for name in ['Right Arm.png','Left Arm.png']:
   arm=Image.open(ROOT/'assets/original'/name).convert('RGBA');d=np.array(arm);r,g,b=d[:,:,:3].astype(float).transpose(2,0,1);region=(r>g*1.3)&(g>b*1.3)&(r>40)
   color={'leather':(72,60,46),'vest':(110,79,52),'plate':(101,82,58)}[kind]
   for k,v in enumerate(color):d[:,:,k]=np.where(region,np.clip(r/108*v,0,255),d[:,:,k])
   outline(Image.fromarray(d)).save(dest/name)
if __name__=='__main__':main()
