"""Keep original complete head artwork registered to the silver reference."""
from pathlib import Path
import json
import unittest
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
class HeadRegistration(unittest.TestCase):
 def test_original_silver_head_is_reference(self):
  config=json.loads((ROOT/'head-registration.json').read_text());silver=config['styles']['silver'];self.assertEqual(silver,{'scaleX':1.0,'offsetX':0.0,'scaleY':1,'offsetY':0})
 def test_lower_face_size_and_position_match_reference(self):
  config=json.loads((ROOT/'head-registration.json').read_text());row=config['landmarkRow']
  target=np.array(Image.open(ROOT/'assets/masks/heads/silver-skin.png'))[:,:,3]>0;ref=np.flatnonzero(target[row])
  for name,placement in config['styles'].items():
   with self.subTest(head=name):
    if name in ('fallen','spectral','guardian'):
     self.assertEqual(placement,{'scaleX':1,'offsetX':0,'scaleY':1,'offsetY':0});continue
    mask_path=ROOT/'assets/masks/packs'/name/'Head-skin.png' if name in ('fallen','spectral','guardian') else ROOT/'assets/masks/heads'/f'{name}-skin.png'
    source=np.array(Image.open(mask_path))[:,:,3]>0;xs=np.flatnonzero(source[row]);scale=placement['scaleX'];offset=placement['offsetX']
    self.assertAlmostEqual(xs[0]*scale+offset,ref[0]);self.assertAlmostEqual(xs[-1]*scale+offset,ref[-1])
    self.assertEqual(placement['scaleY'],1);self.assertEqual(placement['offsetY'],0)
    l,t,r,b=Image.open(ROOT/'assets/packs'/name/'Head.png' if name in ('fallen','spectral','guardian') else ROOT/'assets/heads'/f'{name}.png').getbbox();self.assertGreaterEqual(l*scale+offset,0);self.assertLessEqual(r*scale+offset,480)
if __name__=='__main__':unittest.main()
