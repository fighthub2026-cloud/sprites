"""Keep the complete second pack compatible with the existing native rig."""
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/imported/vector-parts-2'
class SpectralParts(unittest.TestCase):
 def test_all_thirteen_parts_retain_native_dimensions_and_alpha(self):
  self.assertEqual(len(list(SOURCE.glob('*.png'))),13)
  for source in SOURCE.glob('*.png'):
   with self.subTest(part=source.name):
    original=Image.open(source).convert('RGBA');prepared=Image.open(ROOT/'assets/packs/spectral'/source.name).convert('RGBA')
    self.assertEqual(original.size,prepared.size);self.assertTrue(np.array_equal(np.array(original)[:,:,3],np.array(prepared)[:,:,3]))
 def test_animation_keys_are_identical(self):
  def key(e):return e.tag,sorted(e.attrib.items()),[key(c) for c in e]
  imported=ET.parse(SOURCE/'Animations.scml');existing=ET.parse(ROOT/'assets/original/Animations.scml')
  self.assertEqual([key(a)for a in imported.findall('entity/animation')],[key(a)for a in existing.findall('entity/animation')])
 def test_all_expression_brow_fills_preserve_ink(self):
  for name in ['Face 01','Face 02','Face 03']:
   source=np.array(Image.open(SOURCE/(name+'.png')).convert('RGBA'));face=np.array(Image.open(ROOT/'assets/faces/spectral'/(name+'.png')))
   mask=np.array(Image.open(ROOT/'assets/masks/faces/spectral'/(name+'-brows.png')))[:,:,3]>0
   ink=np.all(source[:,:,:3]==[27,26,24],axis=2)&(source[:,:,3]>240)
   self.assertFalse(np.any(mask&ink));self.assertTrue(np.all(face[ink,:3]==[27,26,24]))
   self.assertGreater(np.count_nonzero(mask),1500)
   tones=np.array(Image.open(ROOT/'assets/masks/faces/spectral'/(name+'-brows.png')))[:,:,0]
   self.assertGreater(np.count_nonzero(mask&(tones==128)),1000)
   self.assertGreater(np.count_nonzero(mask&(tones==96)),1000)
 def test_head_materials_are_separate(self):
  skin=np.array(Image.open(ROOT/'assets/masks/packs/spectral/Head-skin.png'))[:,:,3]>0
  hood=np.array(Image.open(ROOT/'assets/masks/packs/spectral/Head-hair.png'))[:,:,3]>0
  self.assertFalse(np.any(skin&hood));self.assertGreater(np.count_nonzero(skin),25000);self.assertGreater(np.count_nonzero(hood),50000)
 def test_upper_brow_is_base_and_lower_brow_is_neutral_shadow(self):
  source=np.array(Image.open(SOURCE/'Face 01.png').convert('RGBA'))
  mask=np.array(Image.open(ROOT/'assets/masks/faces/spectral/Face 01-brows.png'))
  selected=mask[:,:,3]>0
  upper=np.all(source[:,:,:3]==[234,226,223],axis=2)&selected
  lower=np.all(source[:,:,:3]==[175,169,167],axis=2)&selected
  self.assertGreater(np.count_nonzero(upper),1000);self.assertGreater(np.count_nonzero(lower),1000)
  self.assertTrue(np.all(mask[upper,:3]==128));self.assertTrue(np.all(mask[lower,:3]==96))
if __name__=='__main__':unittest.main()
