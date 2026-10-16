"""Build explicit recoloring masks; outlines and other materials stay untouched."""
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
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

def hair_mask(path):
 """Segment material from outline blends, then flatten source texture into tones.

RGB brightness cutoffs miss dark locks and turn tiny source RGB variations into
visible mottling. Fit each pixel to material-to-outline rays instead, retaining
fractional coverage only at their borders.
 """
 d=np.array(Image.open(path).convert('RGBA'));rgb=d[:,:,:3].astype(float)
 ink=np.array([27.,26.,24.]);v=rgb-ink
 palettes={
  'blond':[[250,197,79],[195,151,57],[255,217,111]],
  'blue':[[125,175,226],[86,131,170],[150,199,236]],
  'silver':[[208,210,215],[150,152,157],[232,234,238]],
  'short':[[60,61,64],[51,51,52],[83,87,90]]}
 hair=np.array(palettes[path.stem],dtype=float)
 skin=np.array([[238,200,159],[192,161,125],[218,182,144]],dtype=float)
 candidates=np.concatenate([hair,skin]);directions=candidates-ink
 t=np.clip(np.einsum('hwc,nc->hwn',v,directions)/np.sum(directions**2,axis=1),0,1)
 error=np.sum((v[:,:,None,:]-t[:,:,:,None]*directions[None,None,:,:])**2,axis=3)
 nearest=error.argmin(2);coverage=np.take_along_axis(t,nearest[:,:,None],axis=2)[:,:,0]
 selected=(nearest<3)&(d[:,:,3]>0)&(np.max(abs(v),axis=2)>1)
 outline=np.max(abs(v),axis=2)<=1
 interior=distance_transform_edt(~outline)>1.5
 coverage=np.where(interior,1,coverage)
 # Recover the unblended material luminance before assigning a flat shade.
 lum=np.einsum('hwc,c->hw',rgb,np.array([.2126,.7152,.0722]))
 ink_lum=float(ink @ np.array([.2126,.7152,.0722]));base=float(hair[0] @ np.array([.2126,.7152,.0722]))
 recovered=ink_lum+(lum-ink_lum)/np.maximum(coverage,.01)
 ratio=recovered/base
 shade=np.where(ratio<.88,100,np.where(ratio>1.10,150,128))
 out=np.zeros_like(d);out[:,:,:3]=shade[:,:,None]
 out[:,:,3]=np.where(selected,np.rint(coverage*255),0).astype('uint8')
 dest=ROOT/'assets/masks/heads'/(path.stem+'-hair.png');dest.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(out).save(dest)

def skin_mask(path):
 """Separate skin from ink blends without brightness cutoffs or source grain."""
 d=np.array(Image.open(path).convert('RGBA'));rgb=d[:,:,:3].astype(float)
 ink=np.array([27.,26.,24.]);v=rgb-ink
 bare=path.parent.name=='bare'
 skin=np.array([[219,190,154],[186,162,131],[242,210,170]] if bare else [[238,200,159],[192,161,125],[218,182,144]],dtype=float)
 other={
  'blond':[[250,197,79],[195,151,57],[255,217,111]],
  'blue':[[125,175,226],[86,131,170],[150,199,236]],
  'silver':[[208,210,215],[150,152,157],[232,234,238]],
  'short':[[60,61,64],[51,51,52],[83,87,90]],
  'hood':[[36,79,106],[25,52,70],[47,98,127]]}
 # Use the same material competition as the hair mask so the masks never overlap.
 candidates=np.concatenate([np.array(other[path.stem],dtype=float),skin]) if path.stem in other else skin
 directions=candidates-ink
 t=np.clip(np.einsum('hwc,nc->hwn',v,directions)/np.sum(directions**2,axis=1),0,1)
 error=np.sum((v[:,:,None,:]-t[:,:,:,None]*directions[None,None,:,:])**2,axis=3)
 nearest=error.argmin(2);coverage=np.take_along_axis(t,nearest[:,:,None],axis=2)[:,:,0]
 selected=(d[:,:,3]>0)&(np.max(abs(v),axis=2)>1)
 if path.stem in other:selected&=nearest>=3
 outline=np.max(abs(v),axis=2)<=1
 coverage=np.where(distance_transform_edt(~outline)>1.5,1,coverage)
 weights=np.array([.2126,.7152,.0722]);lum=rgb@weights;ink_lum=float(ink@weights);base=float(skin[0]@weights)
 recovered=ink_lum+(lum-ink_lum)/np.maximum(coverage,.01)
 shade=np.where(recovered/base<.88,100,np.where(recovered/base>1.1,150,128))
 out=np.zeros_like(d);out[:,:,:3]=shade[:,:,None];out[:,:,3]=np.where(selected,np.rint(coverage*255),0).astype('uint8')
 dest=ROOT/'assets/masks'/path.relative_to(ROOT/'assets');dest=dest.with_name(dest.stem+'-skin.png');dest.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(out).save(dest)

def main():
 from prepare_native import register_faces
 register_faces()
 skin=lambda r,g,b:(r>95)&(r>g*1.06)&(g>b*1.09)&(b>g*.53)
 for p in (ROOT/'assets/heads').glob('*.png'):
  skin_mask(p)
  if p.stem!='bald' and p.stem!='hood':
   hair_mask(p)
 for folder in ['focused','adventurer','veteran','ranger']:
  for p in (ROOT/'assets/faces'/folder).glob('*.png'):
   mask(p,'eyes',lambda r,g,b:(g>r*1.4)&(g>b*1.1)&(g>35) if folder in ['focused','ranger'] else ((b>r*1.4)&(b>g*1.15)&(b>45) if folder=='adventurer' else (r>g*1.25)&(g>b*1.4)&(r>45)&(r<160)))
   mask(p,'brows',lambda r,g,b:(r>g*1.35)&(g>b*1.4)&(r>55) if folder!='veteran' else (abs(r-g)<12)&(g>b)&(r>55)&(r<200))
 # Bare hands use the native fist outline, with leather fills replaced by skin.
 for name in ['Right Hand.png','Left Hand.png']:
  im=Image.open(ROOT/'assets/original'/name).convert('RGBA');d=np.array(im);r,g,b=d[:,:,:3].astype(float).transpose(2,0,1);region=(r>g*1.25)&(g>b*1.25)&(r>40)
  for k,v in enumerate([219,190,154]):d[:,:,k]=np.where(region,np.clip(v*r/81,0,255),d[:,:,k])
  dest=ROOT/'assets/hands/bare'/name;dest.parent.mkdir(exist_ok=True,parents=True);Image.fromarray(d).save(dest);skin_mask(dest)
 # Atlas-based expressions own their masks; don't overwrite them with legacy
 # color thresholds when preparing the other materials.
 from prepare_expressions import main as expressions
 expressions()
 from prepare_fallen import main as fallen
 fallen()
 from prepare_spectral import main as spectral
 spectral()
if __name__=='__main__':main()
