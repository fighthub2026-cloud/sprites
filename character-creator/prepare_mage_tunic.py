"""Register the four mage.zip components; hands and legs use the Fallen pack."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt,binary_erosion
from prepare_native import outline

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT/'assets/imported/mage-tunic'

def broad_body():
    """Register newly drawn cloth to the basic torso's exact silhouette."""
    template=Image.open(ROOT/'assets/outfits/basic/Body.png').convert('RGBA')
    alpha=np.array(template)[:,:,3];box=template.getbbox()
    art=Image.open(ROOT/'sources/mage-tunic-body-wide.png').convert('RGBA')
    visible=art.getchannel('A').point(lambda a:255 if a>128 else 0).getbbox()
    art=art.crop(visible).resize((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS)
    registered=Image.new('RGBA',template.size);registered.alpha_composite(art,box[:2])
    d=np.array(registered)
    # Only the new drawing is registered; the old narrow torso is never scaled.
    # Basic's alpha fixes shoulder/chest width and every arm attachment edge.
    d[(alpha>0)&(d[:,:,3]<128),:3]=[75,54,85]
    edge=(alpha>0)&(distance_transform_edt(alpha>0)<=5)
    d[edge,:3]=[27,26,24];d[:,:,3]=alpha
    return outline(Image.fromarray(d))

def main():
    dest = ROOT/'assets/packs/mage-tunic'
    dest.mkdir(parents=True, exist_ok=True)
    for name, size in [('Head.png',(480,480)),('Body.png',(320,320)),
                       ('Left Arm.png',(128,128)),('Right Arm.png',(128,128))]:
        image = broad_body() if name=='Body.png' else Image.open(SOURCE/name).convert('RGBA')
        assert image.size == size, (name,image.size)
        image=outline(image)
        if name=='Head.png':
            d=np.array(image);rgb=d[:,:,:3].astype(float)
            # The supplied head has warm brown raster ink, unlike the older
            # neutral vector packs. Do not classify its ink as exposed skin.
            ink=(rgb.max(2)<120)|(rgb[:,:,1]<rgb[:,:,0]*.67)
            d[ink&(d[:,:,3]>0),:3]=[27,26,24];image=Image.fromarray(d)
        image.save(dest/name)
    d=np.array(Image.open(dest/'Head.png'));rgb=d[:,:,:3].astype(float)
    r,g,b=rgb.transpose(2,0,1);ink=np.all(rgb==[27,26,24],axis=2)
    paint=(d[:,:,3]>0)&~ink
    skin=paint&((r-g)/np.maximum(r,1)>.14)&((g-b)/np.maximum(g,1)>.12)
    # Hair shadows are warm too; classify chroma rather than fitting a peach
    # ray, which incorrectly paints scattered hair/ink pixels as facial skin.
    for material,region,base in [('skin',skin,[252,202,163]),('hair',paint&~skin,[236,218,202])]:
        lum=rgb@np.array([.2126,.7152,.0722]);neutral=np.array(base)@np.array([.2126,.7152,.0722])
        shade=np.where(lum<neutral*.8,100,np.where(lum<neutral*.92,112,np.where(lum>neutral*1.06,134,128)))
        direction=np.array(base)-[27,26,24]
        coverage=np.clip(np.sum((rgb-[27,26,24])*direction,axis=2)/np.sum(direction**2),0,1)
        coverage=np.where(distance_transform_edt(~ink)>1.5,1,coverage)
        mask=np.zeros_like(d);mask[:,:,:3]=shade[:,:,None];mask[:,:,3]=np.where(region,np.rint(coverage*255),0)
        target=ROOT/'assets/masks/packs/mage-tunic'/('Head-'+material+'.png')
        target.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(mask).save(target)
    # Keep antialiased eyebrow edges just inside the skin boundary so they
    # cannot tint the neighboring hair when the face plane is resampled.
    face=np.zeros_like(d);face[:,:,:3]=128;face[:,:,3]=np.where(binary_erosion(skin,iterations=2),255,0)
    Image.fromarray(face).save(ROOT/'assets/masks/packs/mage-tunic/Head-face.png')
    config=json.loads((ROOT/'head-registration.json').read_text())
    config['styles']['mage-tunic']={'scaleX':1,'offsetX':0,'scaleY':1,'offsetY':0}
    (ROOT/'head-registration.json').write_text(json.dumps(config,indent=2)+'\n')
    print('Prepared four mage components at native dimensions; Fallen limbs shared at runtime.')

if __name__=='__main__':main()
