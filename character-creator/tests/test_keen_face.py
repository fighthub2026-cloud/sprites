"""The new eyebrow must be part of the eye island, never a floating stroke."""
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
from scipy.ndimage import label
ROOT=Path(__file__).resolve().parents[1]/'assets'
class FusedEyebrows(unittest.TestCase):
 def test_open_eyebrows_are_connected_to_the_eye(self):
  face=np.array(Image.open(ROOT/'faces/keen/Face 01.png').convert('RGBA'))
  brows=np.array(Image.open(ROOT/'masks/faces/keen/Face 01-brows.png'))[:,:,3]>128
  islands,_=label(face[:,:,3]>128)
  white=(face[:,:,0]>180)&(face[:,:,1]>180)&(face[:,:,2]>160)
  ids=set(islands[brows]);self.assertEqual(len(ids),2)
  for island in ids:
   self.assertNotEqual(island,0);self.assertGreater(np.count_nonzero(white&(islands==island)),30)
 def test_color_masks_never_include_black_contours(self):
  for name in ['Face 01','Face 02','Face 03']:
   with self.subTest(expression=name):
    face=np.array(Image.open(ROOT/'faces/keen'/(name+'.png')).convert('RGBA'))
    ink=np.all(face[:,:,:3]==[27,26,24],axis=2)&(face[:,:,3]>0)
    for material in ['brows','eyes']:
     mask=np.array(Image.open(ROOT/'masks/faces/keen'/(name+'-'+material+'.png')))
     self.assertTrue(np.all(mask[:,:,3][ink]==0))
    brows=np.array(Image.open(ROOT/'masks/faces/keen'/(name+'-brows.png')))[:,:,3]>0
    self.assertGreater(np.count_nonzero(brows),100)
    self.assertTrue(np.all(face[brows,:3]==[78,174,135]))
if __name__=='__main__':unittest.main()
