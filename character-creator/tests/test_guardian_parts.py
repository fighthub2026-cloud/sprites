"""Native shield tracks, artwork and facial materials must survive import."""
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'assets/imported/guardian'

class GuardianParts(unittest.TestCase):
    def test_hair_mask_covers_both_locks_and_excludes_helmet(self):
        mask=np.array(Image.open(ROOT/'assets/masks/packs/guardian/Head-hair.png'))[:,:,3]
        self.assertFalse(np.any(mask[:240]))
        self.assertGreater(np.count_nonzero(mask[240:430,:200]),7000)
        self.assertGreater(np.count_nonzero(mask[280:370,390:430]),600)
        self.assertEqual(mask[270,100],0) # lower metal plate beside the left lock
        self.assertEqual(mask[200,200],0)
        self.assertGreater(mask[300,150],0) # lighter hair band next to the face
        self.assertGreater(mask[300,155],0) # bright strand highlight

    def test_all_pngs_preserve_dimensions_and_alpha(self):
        for source in SOURCE.glob('*.png'):
            with self.subTest(part=source.name):
                a=np.array(Image.open(source).convert('RGBA'))
                b=np.array(Image.open(ROOT/'assets/packs/guardian'/source.name).convert('RGBA'))
                self.assertEqual(a.shape,b.shape)
                self.assertTrue(np.array_equal(a[:,:,3],b[:,:,3]))

    def test_shield_tracks_are_native_and_follow_the_front_hand_bone(self):
        native=ET.parse(SOURCE/'Animations.scml')
        prepared=ET.parse(ROOT/'shield.scml')
        for animation in native.findall('entity/animation'):
            other=next(a for a in prepared.findall('entity/animation') if a.get('name')==animation.get('name'))
            for name in ['Shield','bone_008']:
                a=next(t for t in animation.findall('timeline') if t.get('name')==name)
                b=next(t for t in other.findall('timeline') if t.get('name')==name)
                self.assertEqual([dict(k.attrib)for k in a],[dict(k.attrib)for k in b])
                for x,y in zip(a,b):
                    expected=dict(x[0].attrib)
                    if name=='Shield':expected['file']='13'
                    self.assertEqual(expected,dict(y[0].attrib))
            for key in other.findall('mainline/key'):
                hand=next(r for r in key.findall('object_ref') if r.get('timeline')=='3')
                shield=next(r for r in key.findall('object_ref') if r.get('timeline')=='19')
                bone=next(r for r in key.findall('bone_ref') if r.get('id')==shield.get('parent'))
                self.assertEqual(bone.get('parent'),hand.get('parent'))
                self.assertEqual(bone.get('timeline'),'20')
                self.assertEqual(shield.get('z_index'),'11')

    def test_existing_animation_tracks_are_unchanged(self):
        original=json.loads((ROOT/'rig.json').read_text())
        shield=json.loads((ROOT/'shield-rig.json').read_text())
        self.assertEqual(shield['files']['13']['width'],'160')
        self.assertEqual(shield['files']['13']['height'],'160')
        for old,new in zip(original['animations'],shield['animations']):
            self.assertEqual(old['name'],new['name'])
            for key,track in old['timelines'].items():self.assertEqual(track,new['timelines'][key])

    def test_brow_colors_preserve_black_contours_in_every_expression(self):
        for name in ['Face 01','Face 02','Face 03']:
            face=np.array(Image.open(ROOT/'assets/faces/guardian'/(name+'.png')))
            source=np.array(Image.open(SOURCE/(name+'.png')).convert('RGBA'))
            mask=np.array(Image.open(ROOT/'assets/masks/faces/guardian'/(name+'-brows.png')))
            ink=(source[:,:,:3].max(2)<40)&(source[:,:,3]>240)
            self.assertTrue(np.all(face[ink,:3]==[27,26,24]))
            self.assertFalse(np.any(mask[ink,3]))
            self.assertGreater(np.count_nonzero(mask[:,:,3]),1000)

if __name__=='__main__':unittest.main()
