"""Skin recoloring must be complete, flat, and disjoint from hair and ink."""
from pathlib import Path
import unittest
import numpy as np
from scipy.ndimage import label
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'assets'
class SkinMasks(unittest.TestCase):
 def test_masks_cover_skin_without_hair_or_contours(self):
  for name in ['bald','short','silver','blue','blond']:
   with self.subTest(head=name):
    source=np.array(Image.open(ROOT/'heads'/f'{name}.png').convert('RGBA'))
    mask=np.array(Image.open(ROOT/'masks/heads'/f'{name}-skin.png').convert('RGBA'))
    opaque=source[:,:,3]>0;selected=mask[:,:,3]>0;ink=np.all(source[:,:,:3]==[27,26,24],axis=2)
    self.assertGreater(int(selected.sum()),15000)
    self.assertTrue(np.all(mask[:,:,3][ink|~opaque]==0))
    self.assertTrue(set(np.unique(mask[:,:,0][selected])).issubset({100,128,150}))
    self.assertTrue(np.array_equal(mask[:,:,0],mask[:,:,1]));self.assertTrue(np.array_equal(mask[:,:,1],mask[:,:,2]))
    if name!='bald':
     hair=np.array(Image.open(ROOT/'masks/heads'/f'{name}-hair.png'))
     self.assertFalse(np.any(selected&(hair[:,:,3]>0)))
 def test_bare_hands_use_same_flat_shading(self):
  for name in ['Right Hand','Left Hand']:
   mask=np.array(Image.open(ROOT/'masks/hands/bare'/f'{name}-skin.png'))
   self.assertGreater(np.count_nonzero(mask[:,:,3]),100)
   self.assertTrue(set(np.unique(mask[:,:,0][mask[:,:,3]>0])).issubset({100,128,150}))
 def test_ear_shading_has_no_tiny_bright_islands(self):
  for name in ['bald','short','silver','blue','blond']:
   mask=np.array(Image.open(ROOT/'masks/heads'/f'{name}-skin.png'))
   yy,xx=np.indices(mask.shape[:2]);ear=((xx-115)/55)**2+((yy-325)/75)**2<1
   islands,_=label(ear&(mask[:,:,3]>0)&(mask[:,:,0]>100))
   sizes=np.bincount(islands.ravel())[1:]
   self.assertTrue(np.all(sizes>=32),name)
if __name__=='__main__':unittest.main()
