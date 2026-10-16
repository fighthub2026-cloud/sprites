"""The new cloth drawing must keep the basic torso's real attachment shape."""
from pathlib import Path
import unittest
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

class MageTunicBody(unittest.TestCase):
    def test_shoulder_chest_and_hem_match_basic_pixel_for_pixel(self):
        basic=np.array(Image.open(ROOT/'assets/outfits/basic/Body.png').convert('RGBA'))
        mage=np.array(Image.open(ROOT/'assets/packs/mage-tunic/Body.png').convert('RGBA'))
        self.assertEqual(mage.shape,(320,320,4))
        self.assertTrue(np.array_equal(mage[:,:,3],basic[:,:,3]))

    def test_head_and_arms_keep_uploaded_geometry(self):
        for name in ['Head.png','Left Arm.png','Right Arm.png']:
            source=np.array(Image.open(ROOT/'assets/imported/mage-tunic'/name).convert('RGBA'))
            prepared=np.array(Image.open(ROOT/'assets/packs/mage-tunic'/name).convert('RGBA'))
            self.assertTrue(np.array_equal(source[:,:,3],prepared[:,:,3]),name)

if __name__=='__main__':unittest.main()
