"""Import every Vector Parts texture, preserving the provided rig registration."""
from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import distance_transform_edt,binary_fill_holes,label,find_objects
import json
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'assets/imported/forest-variant'
INK=np.array([27.,26.,24.])
SKIN=np.array([[211,188,180],[180,160,153],[196,165,154],[166,140,130]],float)
HAIR=np.array([[165,157,152],[206,196,190],[231,226,223],[124,118,114]],float)
METAL=np.array([[165,158,154],[142,134,129],[124,116,112],[61,58,57],[40,38,37],[82,78,77]],float)

def material_masks(path,groups):
 d=np.array(Image.open(path).convert('RGBA'));rgb=d[:,:,:3].astype(float);v=rgb-INK
 candidates=np.concatenate([palette for _,palette,_ in groups]);directions=candidates-INK
 t=np.clip(np.einsum('hwc,nc->hwn',v,directions)/np.sum(directions**2,axis=1),0,1)
 error=np.sum((v[:,:,None,:]-t[:,:,:,None]*directions[None,None,:,:])**2,axis=3)
 nearest=error.argmin(2);coverage=np.take_along_axis(t,nearest[:,:,None],axis=2)[:,:,0]
 ink=np.max(abs(v),axis=2)<=1;coverage=np.where(distance_transform_edt(~ink)>1.5,1,coverage)
 start=0
 for name,palette,shades in groups:
  selected=(nearest>=start)&(nearest<start+len(palette))&(d[:,:,3]>0)&~ink
  if name:
   m=np.zeros_like(d);idx=np.clip(nearest-start,0,len(palette)-1);m[:,:,:3]=np.array(shades,dtype='uint8')[idx,None];m[:,:,3]=np.where(selected,np.rint(coverage*255),0)
   dest=ROOT/'assets/masks'/path.relative_to(ROOT/'assets');dest=dest.with_name(dest.stem+'-'+name+'.png');dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(m).save(dest)
  start+=len(palette)

def main():
 dest=ROOT/'assets/packs/fallen';dest.mkdir(parents=True,exist_ok=True)
 for source in SOURCE.glob('*.png'):
  im=Image.open(source).convert('RGBA');d=np.array(im);rgb=d[:,:,:3].astype(int);ink=(rgb.max(2)<=42)&((rgb.max(2)-rgb.min(2))<=14)&(d[:,:,3]>0);d[ink,:3]=INK.astype('uint8');Image.fromarray(d).save(dest/source.name)
 for name in ['Head.png','Body.png','Right Hand.png','Left Hand.png']:
  groups=[('skin',SKIN,[128,108,116,96]),('hair' if name=='Head.png' else None,HAIR,[128,178,219,96]),(None,METAL,[128]*len(METAL))]
  if name=='Head.png':groups=groups[:2]
  material_masks(dest/name,groups)
 # The source rig uses file 11=Face03 (hurt), file12=Face02 (blink).
 # Keep the exact same filenames: the existing rig uses those slots too.
 faces=ROOT/'assets/faces/fallen';faces.mkdir(parents=True,exist_ok=True)
 # Preserve the supplied native facial scale and registration. Reducing it to
 # the older catalog plane made the eyes, brows, nose and mouth too small.
 sx=sy=1;tx=ty=0
 for target,source in [('Face 01.png','Face 01.png'),('Face 02.png','Face 02.png'),('Face 03.png','Face 03.png')]:
  im=Image.open(SOURCE/source).convert('RGBA').transform((320,240),Image.Transform.AFFINE,(1/sx,0,-tx/sx,0,1/sy,-ty/sy),Image.Resampling.BICUBIC)
  d=np.array(im);r,g,b=d[:,:,:3].astype(float).transpose(2,0,1);opaque=d[:,:,3]>0
  ink=opaque&(np.maximum.reduce([r,g,b])<43);d[ink,:3]=INK.astype('uint8')
  # The open eyebrow has a transparent enclosed interior. That is the fill;
  # the dark pixels surrounding it are the contour and must stay charcoal.
  if target=='Face 01.png':
   alpha=d[:,:,3]>128;holes=binary_fill_holes(alpha)&~alpha
   labels,_=label(holes);brows=np.zeros_like(alpha)
   for component,box in enumerate(find_objects(labels)):
    if box is not None and box[0].stop<=110 and np.count_nonzero(labels[box]==component+1)>20:
     brows|=labels==component+1
   d[brows,3]=255
  else:
   # Closed expressions have a solid eyebrow stroke. Follow only its upper
   # run in each column, never the eye/lash below it or a horizontal y cutoff.
   dark=(d[:,:,3]>128)&(np.maximum.reduce([r,g,b])<75)
   upper=np.zeros_like(dark)
   for x in range(320):
    rows=np.flatnonzero(dark[53:135,x])+53
    if not len(rows) or rows[0]>125:continue
    start=int(rows[0]);end=start
    while end<160 and dark[end,x]:end+=1
    upper[start:end,x]=True
   brows=distance_transform_edt(upper)>2.5
  eyes=opaque&(b>r*1.2)&(g>r*1.08)&(b>g*1.04)&(b>65)&~brows
  for material,region,base in [('brows',brows,[165,157,152]),('eyes',eyes,[146,190,217])]:
   d[region,:3]=base;m=np.zeros_like(d);m[:,:,:3]=128;m[:,:,3]=np.where(region,d[:,:,3],0)
   path=ROOT/'assets/masks/faces/fallen'/(Path(target).stem+'-'+material+'.png');path.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(m).save(path)
  Image.fromarray(d).save(faces/target)
 config=json.loads((ROOT/'head-registration.json').read_text());target=np.array(Image.open(ROOT/'assets/masks/heads/silver-skin.png'))[:,:,3]>0;src=np.array(Image.open(ROOT/'assets/masks/packs/fallen/Head-skin.png'))[:,:,3]>0
 a=np.flatnonzero(target[390]);b=np.flatnonzero(src[390]);scale=float((a[-1]-a[0])/(b[-1]-b[0]));offset=float(a[0]-b[0]*scale)
 config['styles']['fallen']={'scaleX':scale,'offsetX':offset,'scaleY':1,'offsetY':0};(ROOT/'head-registration.json').write_text(json.dumps(config,indent=2)+'\n')
 print('Imported 13 textures, 3 registered expressions and skin/hair/eye/brow masks.')
if __name__=='__main__':main()
