"""Verify complete source import, native geometry, masks and expression slots."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/imported/forest-variant'
class ImportedParts(unittest.TestCase):
 def test_all_thirteen_original_parts_are_present(self):
  self.assertEqual(len(list(SOURCE.glob('*.png'))),13)
  for src in SOURCE.glob('*.png'):
   prepared=Image.open(ROOT/'assets/packs/fallen'/src.name).convert('RGBA');original=Image.open(src).convert('RGBA')
   self.assertEqual(prepared.size,original.size)
   self.assertTrue(np.array_equal(np.array(prepared)[:,:,3],np.array(original)[:,:,3]),src.name)
 def test_animation_keys_match_existing_rig(self):
  def key(e):return e.tag,sorted(e.attrib.items()),[key(c) for c in e]
  src=ET.parse(SOURCE/'Animations.scml').getroot();existing=ET.parse(ROOT/'assets/original/Animations.scml').getroot()
  self.assertEqual([key(a) for a in src.findall('entity/animation')],[key(a) for a in existing.findall('entity/animation')])
  self.assertEqual(src.find("folder/file[@id='11']").get('name'),'Face 03.png')
  self.assertEqual(existing.find("folder/file[@id='11']").get('name'),'Face 03.png')
 def test_materials_preserve_black_armor_and_hands(self):
  for name in ['Head','Body','Right Hand','Left Hand']:
   src=np.array(Image.open(ROOT/'assets/packs/fallen'/(name+'.png')).convert('RGBA'));m=np.array(Image.open(ROOT/'assets/masks/packs/fallen'/(name+'-skin.png')))
   ink=np.all(src[:,:,:3]==[27,26,24],axis=2)&(src[:,:,3]>0)
   self.assertTrue(np.all(m[:,:,3][ink]==0));self.assertGreater(np.count_nonzero(m[:,:,3]),200)
   if name=='Head':
    hair=np.array(Image.open(ROOT/'assets/masks/packs/fallen/Head-hair.png'))
    self.assertFalse(np.any((hair[:,:,3]>0)&(m[:,:,3]>0)))
 def test_open_brow_mask_fills_holes_and_preserves_original_ink(self):
  sx=204/232;sy=129/152;tx=60-47*sx;ty=53-42*sy
  original=np.array(Image.open(SOURCE/'Face 01.png').convert('RGBA').transform((320,240),Image.Transform.AFFINE,(1/sx,0,-tx/sx,0,1/sy,-ty/sy),Image.Resampling.BICUBIC))
  actual=np.array(Image.open(ROOT/'assets/faces/fallen/Face 01.png').convert('RGBA'))
  mask=np.array(Image.open(ROOT/'assets/masks/faces/fallen/Face 01-brows.png'))[:,:,3]>0
  self.assertGreater(np.count_nonzero(mask),1000)
  self.assertTrue(np.all(original[:,:,3][mask]<=128))
  self.assertTrue(np.all(actual[:,:,3][mask]==255))
  ink=(original[:,:,:3].max(2)<43)&(original[:,:,3]>250)
  self.assertFalse(np.any(ink&mask));self.assertTrue(np.all(actual[ink,:3]==[27,26,24]))
if __name__=='__main__':unittest.main()
