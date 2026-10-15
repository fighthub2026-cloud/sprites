"""Register three sets of facial expressions and their independent color masks."""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label,find_objects
ROOT=Path(__file__).resolve().parent

def main():
 atlas=Image.open(ROOT/'sources/expression-options.png').convert('RGBA')
 for col,profile in enumerate(['focused','adventurer','veteran']):
  for row,name in enumerate(['Face 01.png','Face 03.png','Face 02.png']):
   # Row bands include the whole mouth, unlike equal grid slices.
   top,bottom=[(100,380),(410,670),(700,970)][row]
   cell=atlas.crop((col*512,top,(col+1)*512,bottom));d=np.array(cell);d[:,:,3]=np.where(d[:,:,3]>160,255,0);cell=Image.fromarray(d);box=cell.getchannel('A').getbbox()
   cell=cell.crop(box).resize((204,129),Image.Resampling.LANCZOS);out=Image.new('RGBA',(320,240));out.paste(cell,(60,53))
   d=np.array(out);r,g,b=d[:,:,:3].astype(float).transpose(2,0,1);opaque=d[:,:,3]>0
   ink=(np.maximum.reduce([r,g,b])<45)&opaque
   d[ink,:3]=[27,26,24]
   # Color components are isolated by the charcoal outline; classify brows by
   # their top position, not the RGB of irises or the user's eventual palette.
   if col==0:
    colored=(((r<110)&(g<110)&(b<110))|((g>r*1.12)&(g>b*1.2)))
   elif col==1:
    colored=(b>r*1.35)&(b>g*1.1)
   else:
    colored=((r>g*1.15)&(g>b*1.4))|((b>r*1.3)&(b>g*1.1))
   colored&=opaque&(np.maximum.reduce([r,g,b])>45)
   labels,_=label(colored);brows=np.zeros_like(opaque);eyes=np.zeros_like(opaque)
   for i,sl in enumerate(find_objects(labels)):
    if sl is None:continue
    area=np.count_nonzero(labels[sl]==i+1)
    if area<4:continue
    region=labels==i+1
    target=brows if sl[0].start<88 else eyes
    target|=region
   # Uniform base colors; retain a neutral dark shadow without source grain.
   for material,region,base in [('brows',brows,[(70,73,76),(110,170,211),(176,134,45)][col]),('eyes',eyes,[(96,112,49),(52,119,160),(57,103,131)][col])]:
    lum=.2126*r+.7152*g+.0722*b;median=np.median(lum[region]) if region.any() else 1
    shade=np.where(lum<median*.78,108,128)
    for k in range(3):d[:,:,k]=np.where(region,np.array(base)[k]*shade/128,d[:,:,k])
    m=np.zeros_like(d);m[:,:,:3]=shade[:,:,None];m[:,:,3]=np.where(region,d[:,:,3],0)
    dest=ROOT/'assets/masks/faces'/profile/(Path(name).stem+'-'+material+'.png');dest.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(m).save(dest)
   dest=ROOT/'assets/faces'/profile/name;dest.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(d).save(dest)
 print('Registered 3 facial styles × 3 expressions with brow/iris masks.')
if __name__=='__main__':main()
