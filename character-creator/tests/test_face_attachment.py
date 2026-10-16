"""Face clipping stays registered during every action and expression swap."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class FaceAttachment(unittest.TestCase):
 def test_head_and_face_share_a_parent_and_fixed_texture_transforms(self):
  rig=json.loads((ROOT/'rig.json').read_text());reference={}
  for animation in rig['animations']:
   for timeline in animation['timelines'].values():
    for key in timeline:
     value=key['transform'];file=value.get('file')
     if file not in ['1','4','11','12']:continue
     role='head' if file=='1' else 'face'
     transform=tuple(float(value.get(k,default)) for k,default in [('x',0),('y',0),('angle',0),('scale_x',1),('scale_y',1),('pivot_x',0),('pivot_y',1)])
     reference.setdefault(role,transform);self.assertEqual(transform,reference[role],animation['name'])
   for key in animation['mainline']:
    head=next(ref for ref in key['objects'] if ref['timeline']=='1');face=next(ref for ref in key['objects'] if ref['timeline']=='6')
    self.assertEqual(head.get('parent'),face.get('parent'),animation['name'])
if __name__=='__main__':unittest.main()
