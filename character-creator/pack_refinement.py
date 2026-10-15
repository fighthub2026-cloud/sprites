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
    # Outfit geometry and expressions must always come from the original rig.
    from prepare_native import main as prepare_native
    prepare_native()
    print('Packed 6 heads; preserved native outfit silhouettes and animated expressions.')

if __name__=='__main__':main()
