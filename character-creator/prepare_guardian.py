"""Prepare Valkyrie parts and transfer its independent shield rig unchanged."""
from copy import deepcopy
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes, label, find_objects
from prepare_fallen import material_masks, INK
from prepare_native import outline

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'assets/imported/guardian'
SKIN = np.array([[196,153,110],[154,121,88],[172,135,98]],float)
METAL = np.array([[115,115,107],[82,83,77],[130,130,122],
                  [151,146,134],[99,92,77],[126,115,94]],float)

def rig_json(root):
    rig = {'files': {f.get('id'):dict(f.attrib) for f in root.findall('folder/file')},
           'animations': [], 'frameCounts': json.loads((ROOT/'rig.json').read_text())['frameCounts']}
    for animation in root.findall('entity/animation'):
        item = dict(animation.attrib)
        item['mainline'] = [dict(k.attrib, bones=[dict(r.attrib) for r in k.findall('bone_ref')],
                                 objects=[dict(r.attrib) for r in k.findall('object_ref')])
                            for k in animation.findall('mainline/key')]
        item['timelines'] = {t.get('id'): [dict(k.attrib, transform=dict(k[0].attrib)) for k in t.findall('key')]
                             for t in animation.findall('timeline')}
        rig['animations'].append(item)
    return rig

def shield_rig():
    native = ET.parse(SOURCE/'Animations.scml').getroot()
    root = ET.parse(ROOT/'assets/original/Animations.scml').getroot()
    file = deepcopy(next(f for f in native.findall('folder/file') if f.get('name')=='Shield.png'))
    file.set('id','13');root.find('folder').append(file)
    entity = root.find('entity')
    info = deepcopy(next(i for i in native.findall('entity/obj_info') if i.get('name')=='bone_008'))
    entity.insert(0,info)
    for animation in entity.findall('animation'):
        source = next(a for a in native.findall('entity/animation') if a.get('name')==animation.get('name'))
        bone = deepcopy(next(t for t in source.findall('timeline') if t.get('name')=='bone_008'))
        shield = deepcopy(next(t for t in source.findall('timeline') if t.get('name')=='Shield'))
        bone.set('id','20');shield.set('id','19')
        for obj in shield.findall('key/object'):obj.set('file','13')
        mainline = animation.find('mainline');keys = list(mainline)
        # Preserve original key transitions and add any shield-specific transitions.
        times = sorted({int(k.get('time','0')) for k in keys} |
                       {int(k.get('time','0')) for t in [bone,shield] for k in t.findall('key')})
        mainline.clear()
        for index,time in enumerate(times):
            if time>=int(animation.get('length')):continue
            key = deepcopy(max((k for k in keys if int(k.get('time','0'))<=time),key=lambda k:int(k.get('time','0'))))
            key.set('id',str(index));key.set('time',str(time))
            parent = next(r for r in key.findall('object_ref') if r.get('timeline')=='3').get('parent')
            def key_at(t):
                return max((k for k in t.findall('key') if int(k.get('time','0'))<=time),key=lambda k:int(k.get('time','0'))).get('id')
            ET.SubElement(key,'bone_ref',id='8',parent=parent,timeline='20',key=key_at(bone))
            ET.SubElement(key,'object_ref',id='11',parent='8',timeline='19',key=key_at(shield),z_index='11')
            mainline.append(key)
        animation.extend([shield,bone])
    ET.indent(root)
    (ROOT/'shield.scml').write_text(ET.tostring(root,encoding='unicode'))
    (ROOT/'shield-rig.json').write_text(json.dumps(rig_json(root),separators=(',',':')))

def main():
    dest = ROOT/'assets/packs/guardian';dest.mkdir(parents=True,exist_ok=True)
    for source in SOURCE.glob('*.png'):outline(Image.open(source)).save(dest/source.name)
    trident = Image.open(SOURCE/'Weapon.png').convert('RGBA').rotate(180)
    trident = trident.crop(trident.getbbox());trident.thumbnail((344,118),Image.Resampling.LANCZOS)
    weapon = Image.new('RGBA',(400,128));weapon.alpha_composite(trident,(28,(128-trident.height)//2))
    weapon.save(ROOT/'assets/accessories/GuardianTrident.png')
    hair_palette=np.vstack([METAL,[[182,176,162],[219,216,209]]])
    material_masks(dest/'Head.png',[('skin',SKIN,[128,100,112]),('hair',hair_palette,[128,96,138,134,88,116,134,142]),
                                   (None,np.array([[230,157,151]],float),[128])])
    # Hair and helmet share the source grey palette. Their ink boundaries
    # separate the two exposed locks, so only those regions are recolorable.
    hair_path=ROOT/'assets/masks/packs/guardian/Head-hair.png'
    hair=np.array(Image.open(hair_path));components,_=label(hair[:,:,3]>0)
    locks=components[340,120],components[320,404]
    assert all(locks), 'Both native hair locks must be found'
    exposed=np.isin(components,locks)
    from scipy.ndimage import distance_transform_edt
    yy,_=np.indices(exposed.shape)
    # Retain nearby antialias fragments without crossing the thick helmet rim.
    exposed=(distance_transform_edt(~exposed)<=2)&(yy>=240)
    hair[~exposed,3]=0;Image.fromarray(hair).save(hair_path)
    material_masks(dest/'Body.png',[('skin',SKIN,[128,100,112]),(None,METAL,[128]*len(METAL))])
    faces = ROOT/'assets/faces/guardian';faces.mkdir(parents=True,exist_ok=True)
    for name in ['Face 01.png','Face 02.png','Face 03.png']:
        d = np.array(outline(Image.open(SOURCE/name)))
        rgb = d[:,:,:3].astype(float);r,g,b = rgb.transpose(2,0,1)
        brows = (abs(r-108)<12)&(abs(g-83)<12)&(abs(b-61)<12)&(d[:,:,3]>0)
        holes = binary_fill_holes(d[:,:,3]>128)&(d[:,:,3]<=128)
        components,_ = label(holes)
        for i,box in enumerate(find_objects(components)):
            if box is not None and box[0].stop<120 and np.count_nonzero(components[box]==i+1)>30:
                brows |= components==i+1
        eyes = (d[:,:,3]>0)&(g>r*1.15)&(b>r*1.1)&(g>b)&(g>40)&~brows
        # Filled brows keep their original solid black arch in all expressions.
        d[brows,3] = 255
        for material,region,base in [('brows',brows,[108,83,61]),('eyes',eyes,[61,81,75])]:
            d[region,:3] = base
            mask = np.zeros_like(d);mask[:,:,:3] = 128;mask[:,:,3] = np.where(region,d[:,:,3],0)
            target = ROOT/'assets/masks/faces/guardian'/(Path(name).stem+'-'+material+'.png')
            target.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(mask).save(target)
        Image.fromarray(d).save(faces/name)
    config = json.loads((ROOT/'head-registration.json').read_text())
    config['styles']['guardian'] = {'scaleX':1,'offsetX':0,'scaleY':1,'offsetY':0}
    (ROOT/'head-registration.json').write_text(json.dumps(config,indent=2)+'\n')
    shield_rig()
    print('Prepared Valkyrie components, native expressions and independent animated shield.')

if __name__=='__main__':main()
