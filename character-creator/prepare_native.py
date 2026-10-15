"""Preserve native silhouettes, facial registration and weapon attack reach."""
from pathlib import Path
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parent
PARTS=['Body.png','Right Arm.png','Left Arm.png','Right Hand.png','Left Hand.png','Right Leg.png','Left Leg.png']
def outline(im):
    d=np.array(im.convert('RGBA'));rgb=d[:,:,:3];mask=(rgb.max(2)<=42)&((rgb.max(2).astype(int)-rgb.min(2))<=14)&(d[:,:,3]>0)
    d[mask,:3]=[27,26,24]
    return Image.fromarray(d)
def main():
    for path in (ROOT/'assets/heads').glob('*.png'):outline(Image.open(path)).save(path)
    for kind,color in [('basic',(99,75,49)),('mage',(54,64,73))]:
        dest=ROOT/'assets/outfits'/kind;dest.mkdir(exist_ok=True,parents=True)
        for name in PARTS:
            im=Image.open(ROOT/'assets/original'/name).convert('RGBA');d=np.array(im);rgb=d[:,:,:3].astype(float);r,g,b=rgb.transpose(2,0,1)
            cloth=(g>r*1.15)&(g>b*1.6)&(d[:,:,3]>0)
            rgb[cloth]=np.clip((g[cloth]/75)[:,None]*np.array(color),0,255)
            if kind=='mage' and ('Arm' in name or name=='Body.png'):
                leather=(r>g*1.3)&(g>b*1.3)&(r>40)&(d[:,:,3]>0)
                if name=='Body.png':leather[180:,:]=False
                rgb[leather]=np.clip((r[leather]/108)[:,None]*np.array(color),0,255)
            d[:,:,:3]=rgb.astype('uint8');outline(Image.fromarray(d)).save(dest/name)
    # One affine registration shared by all expressions, including closed eyes.
    for profile in ['ranger','focused','adventurer','veteran']:
        dest=ROOT/'assets/faces'/profile;dest.mkdir(exist_ok=True,parents=True)
        for name in ['Face 01.png','Face 02.png','Face 03.png']:
            im=Image.open(ROOT/'assets/original'/name).convert('RGBA');d=np.array(im);rgb=d[:,:,:3].astype(float);r,g,b=rgb.transpose(2,0,1)
            if profile!='ranger':
                eyes=(g>r*1.4)&(g>b*1.1)&(g>35)
                target={'focused':(20,93,68),'adventurer':(38,96,151),'veteran':(151,104,37)}[profile]
                rgb[eyes]=np.clip((g[eyes]/93)[:,None]*np.array(target),0,255)
                if profile=='veteran':
                    brows=(r>g*1.35)&(g>b*1.4)&(r>55)
                    rgb[brows]=np.clip((r[brows]/165)[:,None]*np.array([179,177,163]),0,255)
            d[:,:,:3]=rgb.astype('uint8');im=Image.fromarray(d)
            sx=204/258;tx=60-22*sx
            im=im.transform((320,240),Image.Transform.AFFINE,(1/sx,0,-tx/sx,0,1,-4),Image.Resampling.BICUBIC)
            outline(im).save(dest/name)
    # Match native texture bounds, so native pivots give every weapon full reach.
    for name in ['Staff.png','Club.png']:
        path=ROOT/'assets/accessories'/name;im=Image.open(path).convert('RGBA');box=im.getchannel('A').getbbox()
        out=Image.new('RGBA',(400,128));out.paste(im.crop(box).resize((344,70),Image.Resampling.LANCZOS),(28,29));outline(out).save(path)
if __name__=='__main__':main()
