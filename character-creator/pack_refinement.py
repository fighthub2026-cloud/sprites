"""Register the new rounded head and coordinated mage atlas into rig textures.

Requires Pillow, NumPy, SciPy and ImageMagick. Alpha thresholding removes the
faint export halos before resizing; geometry inside each part is not redrawn.
"""
from pathlib import Path
import subprocess
from PIL import Image
from scipy import ndimage
import numpy as np

ROOT=Path(__file__).resolve().parent

def parts(path,cols,rows):
    image=Image.open(path)
    alpha=np.array(image.getchannel('A'))>128
    labels,_=ndimage.label(alpha)
    result={}
    for index,slice_ in enumerate(ndimage.find_objects(labels)):
        if slice_ is None:continue
        area=int(np.count_nonzero(labels[slice_]==index+1))
        if area<5000:continue
        left,top,right,bottom=slice_[1].start,slice_[0].start,slice_[1].stop,slice_[0].stop
        col=int((left+right)/2/image.width*cols);row=int((top+bottom)/2/image.height*rows)
        slot=row*cols+col
        if slot not in result or area>result[slot][0]:result[slot]=(area,(left,top,right,bottom))
    return {slot:value[1] for slot,value in result.items()}

def pack(path,box,destination,size,target):
    destination.parent.mkdir(parents=True,exist_ok=True)
    l,t,r,b=box;x,y,w,h=target
    subprocess.run(['convert',str(path),'-channel','A','-threshold','50%','+channel',
                    '-crop',f'{r-l}x{b-t}+{l}+{t}','+repage','-resize',f'{w}x{h}!',
                    '-background','none','-gravity','NorthWest','-extent',
                    f'{size[0]}x{size[1]}-{x}-{y}',str(destination)],check=True)

def main():
    source=ROOT/'sources/head-options.png';heads=parts(source,3,2)
    assert len(heads)==6
    for slot,name in enumerate(['bald','short','blue','blond','silver','hood']):
        pack(source,heads[slot],ROOT/'assets/heads'/f'{name}.png',(480,480),(65,65,370,365))
    source=ROOT/'sources/mage-parts.png';mage=parts(source,4,2)
    assert len(mage)==8
    mapping=[('Body.png',(320,320),(65,53,190,213)),
             ('Right Arm.png',(128,128),(18,23,80,89)),
             ('Left Arm.png',(128,128),(33,27,77,87)),
             ('Right Hand.png',(128,128),(23,22,82,84)),
             ('Left Hand.png',(128,128),(28,29,73,70)),
             ('Right Leg.png',(128,128),(24,23,80,82)),
             ('Left Leg.png',(128,128),(25,25,78,78)),
             ('Staff.png',(400,128),(65,24,320,80))]
    for slot,(name,size,target) in enumerate(mapping):
        destination=ROOT/'assets/outfits/mage'/name if name!='Staff.png' else ROOT/'assets/accessories/Staff.png'
        pack(source,mage[slot],destination,size,target)
    # Keep all expressions inside the same smaller blank facial plane.
    source=ROOT/'sources/face-options.png';image=Image.open(source);width,height=image.size
    for i,name in enumerate(['focused','adventurer','veteran']):
        cell=image.crop((i*width//3,0,(i+1)*width//3,height))
        l,t,r,b=cell.getchannel('A').point(lambda a:255 if a>128 else 0).getbbox()
        pack(source,(i*width//3+l,t,i*width//3+r,b),ROOT/'assets/faces'/f'{name}.png',(320,240),(60,65,204,129))
    for name in ['Face 01.png','Face 02.png','Face 03.png']:
        source=ROOT/'assets/original'/name
        box=Image.open(source).getchannel('A').point(lambda a:255 if a>128 else 0).getbbox()
        pack(source,box,ROOT/'assets/faces/ranger'/name,(320,240),(60,65,204,129))
    print('Packed 6 rounded heads, 8 coordinated mage parts and 6 face textures.')

if __name__=='__main__':main()
