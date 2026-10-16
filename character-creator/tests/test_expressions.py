"""Facial atlases must retain transparent registration and isolated materials."""
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'assets'
class ExpressionParts(unittest.TestCase):
 def test_registered_expressions_and_materials(self):
  for profile in ['focused','adventurer','veteran']:
   images=[]
   for name in ['Face 01','Face 02','Face 03']:
    with self.subTest(profile=profile,expression=name):
     im=Image.open(ROOT/'faces'/profile/(name+'.png')).convert('RGBA');self.assertEqual(im.size,(320,240));a=np.array(im);images.append(a.tobytes())
     l,t,r,b=im.getchannel('A').getbbox();stroke=0;self.assertGreaterEqual(l,47-stroke);self.assertGreaterEqual(t,42-stroke);self.assertLessEqual(r,279+stroke);self.assertLessEqual(b,194+stroke)
     white=(a[:,:,0]>180)&(a[:,:,1]>180)&(a[:,:,2]>160)&(a[:,:,3]>240)
     masks=[]
     for material in ['eyes','brows']:
      m=np.array(Image.open(ROOT/'masks/faces'/profile/(name+'-'+material+'.png')))
      self.assertTrue(np.all(m[:,:,3][white]==0),'White sclera cannot be recolored')
      self.assertTrue(np.all(m[:,:,3][a[:,:,3]==0]==0));masks.append(m[:,:,3]>0)
     self.assertFalse(np.any(masks[0]&masks[1]),'Brow and iris masks must be independent')
   self.assertEqual(len(set(images)),3)
 def test_every_face_uses_the_enlarged_plane(self):
  for profile in ['focused','adventurer','veteran','ranger','fallen']:
   with self.subTest(profile=profile):
    im=Image.open(ROOT/'faces'/profile/'Face 01.png').convert('RGBA')
    l,t,r,b=im.getchannel('A').getbbox()
    self.assertGreaterEqual(r-l,230);self.assertLessEqual(r-l,234)
    self.assertGreaterEqual(b-t,150);self.assertLessEqual(b-t,154)
    self.assertAlmostEqual((l+r)/2,163,delta=1)
    self.assertAlmostEqual((t+b)/2,118,delta=1)
if __name__=='__main__':unittest.main()
