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
if __name__=='__main__':unittest.main()
