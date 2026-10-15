"""Build explicit recoloring masks; outlines and other materials stay untouched."""
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def mask(path,material,choose):
 im=Image.open(path).convert('RGBA');d=np.array(im);r,g,b=d[:,:,:3].astype(float).transpose(2,0,1)
 selected=choose(r,g,b)&(d[:,:,3]>0)
 lum=.2126*r+.7152*g+.0722*b
 values=lum[selected & (d[:,:,3]>240)]
 if not len(values):return
 # Dominant flat fill is the neutral material; other tones become overlays.
 hist=np.bincount(np.rint(values).astype(int),minlength=256);base=max(1,int(hist.argmax()))
 shade=np.where(lum<=base,128*lum/base,128+127*(lum-base)/max(1,255-base))
 out=np.zeros_like(d);out[:,:,:3]=np.clip(shade,0,255).astype('uint8')[:,:,None];out[:,:,3]=np.where(selected,d[:,:,3],0)
 dest=ROOT/'assets/masks'/path.relative_to(ROOT/'assets');dest=dest.with_name(dest.stem+'-'+material+'.png');dest.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(out).save(dest)

def main():
 skin=lambda r,g,b:(r>95)&(r>g*1.06)&(g>b*1.09)&(b>g*.53)
 for p in (ROOT/'assets/heads').glob('*.png'):
  mask(p,'skin',skin)
  if p.stem!='bald' and p.stem!='hood':
   mask(p,'hair',lambda r,g,b:~skin(r,g,b)&(np.maximum.reduce([r,g,b])>43))
 for folder in ['focused','adventurer','veteran','ranger']:
  for p in (ROOT/'assets/faces'/folder).glob('*.png'):
   mask(p,'eyes',lambda r,g,b:(g>r*1.4)&(g>b*1.1)&(g>35) if folder in ['focused','ranger'] else ((b>r*1.4)&(b>g*1.15)&(b>45) if folder=='adventurer' else (r>g*1.25)&(g>b*1.4)&(r>45)&(r<160)))
   mask(p,'brows',lambda r,g,b:(r>g*1.35)&(g>b*1.4)&(r>55) if folder!='veteran' else (abs(r-g)<12)&(g>b)&(r>55)&(r<200))
 # Bare hands use the native fist outline, with leather fills replaced by skin.
 for name in ['Right Hand.png','Left Hand.png']:
  im=Image.open(ROOT/'assets/original'/name).convert('RGBA');d=np.array(im);r,g,b=d[:,:,:3].astype(float).transpose(2,0,1);region=(r>g*1.25)&(g>b*1.25)&(r>40)
  for k,v in enumerate([219,190,154]):d[:,:,k]=np.where(region,np.clip(v*r/81,0,255),d[:,:,k])
  dest=ROOT/'assets/hands/bare'/name;dest.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(d).save(dest);mask(dest,'skin',skin)
if __name__=='__main__':main()
