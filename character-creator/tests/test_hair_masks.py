"""Regression checks for complete hair masks and neutral flat shading."""
import unittest
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class HairMasks(unittest.TestCase):
 def test_flat_shading_and_outline_preservation(self):
  for name in ['blond','blue','short','silver']:
   with self.subTest(head=name):
    source=np.array(Image.open(ROOT/'assets/heads'/f'{name}.png').convert('RGBA'))
    mask=np.array(Image.open(ROOT/'assets/masks/heads'/f'{name}-hair.png').convert('RGBA'))
    ink=np.all(source[:,:,:3]==[27,26,24],axis=2)&(source[:,:,3]>0)
    self.assertTrue(np.all(mask[:,:,3][ink]==0))
    selected=mask[:,:,3]>0
    self.assertGreater(int(selected.sum()),30000)
    self.assertTrue(set(np.unique(mask[:,:,0][selected])).issubset({100,128,150}))
    self.assertTrue(np.array_equal(mask[:,:,0],mask[:,:,1]))
    self.assertTrue(np.array_equal(mask[:,:,1],mask[:,:,2]))
    self.assertTrue(np.all(mask[:,:,3][source[:,:,3]==0]==0))
 def test_dark_hair_shadow_is_included(self):
  source=np.array(Image.open(ROOT/'assets/heads/short.png').convert('RGBA'))
  mask=np.array(Image.open(ROOT/'assets/masks/heads/short-hair.png').convert('RGBA'))
  # Interior dark locks cannot be dropped by the old brightness >43 cutoff.
  dark=(source[:,:,0]>28)&(source[:,:,0]<43)&(source[:,:,2]>=source[:,:,0])&(source[:,:,3]==255)
  self.assertGreater(int(dark.sum()),30)
  self.assertGreater(float(np.mean(mask[:,:,3][dark]>0)),.95)
if __name__=='__main__':unittest.main()
