"""Fail early on invalid edit timing and check subject/caption beat selection."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from direction import validate_direction,beat_at,caption_y
from story import load_story,StoryError


class DirectionTests(unittest.TestCase):
    def setUp(self):
        self.shots=[{'id':'S01','duration_s':4.,'start':0}]
        self.doc={'schema_version':1,'shots':{'S01':[{'at':0,'view':'pump'},
                  {'at':1.5,'view':'cylinder','move':.4},{'at':3,'view':'lift'}]}}

    def test_cut_and_travel_have_distinct_boundaries(self):
        beats=validate_direction(self.doc,self.shots,'garage',30)['S01']
        self.assertEqual(beat_at(beats,1.49,4)[0]['view'],'pump')
        beat,previous,amount,_=beat_at(beats,1.7,4)
        self.assertEqual((beat['view'],previous['view']),('cylinder','pump'))
        self.assertAlmostEqual(amount,.5)
        self.assertEqual(beat_at(beats,3.,4)[2],1)
        self.assertEqual(beat_at(beats,3.,4)[0]['view'],'lift')

    def test_invalid_edits_rejected_before_blender(self):
        cases=[ [{'at':.1,'view':'pump'}], [{'at':0,'view':'pump','move':.1}],
                [{'at':0,'view':'unknown'}], [{'at':0,'view':'pump','scale':float('nan')}],
                [{'at':0,'view':'pump','at_typo':1}],
                [{'at':0,'view':'pump'},{'at':.05,'view':'line'}],
                [{'at':0,'view':'pump'},{'at':4,'view':'line'}],
                [{'at':0,'view':'pump'},{'at':2,'view':'line','move':1},{'at':2.5,'view':'lift'}],
                [{'at':0,'view':'pump'},{'at':1,'view':'line'},{'at':1,'view':'lift'}] ]
        for beats in cases:
            with self.subTest(beats=beats):
                doc={'schema_version':1,'shots':{'S01':beats}}
                with self.assertRaises(ValueError):validate_direction(doc,self.shots,'garage',30)

    def test_unknown_shots_and_template_specific_subjects_rejected(self):
        doc=copy.deepcopy(self.doc);doc['shots']['S99']=doc['shots'].pop('S01')
        with self.assertRaisesRegex(ValueError,'unknown'):validate_direction(doc,self.shots,'garage',30)
        doc={'schema_version':1,'shots':{'S01':[{'at':0,'view':'sensor'}]}}
        with self.assertRaisesRegex(ValueError,'unsupported'):validate_direction(doc,self.shots,'hydraulic_lab',30)

    def test_caption_safe_zone_changes_at_exact_cut(self):
        beats=validate_direction(self.doc,self.shots,'garage',30)['S01']
        shot={**self.shots[0],'start':10.,'direction':beats}
        self.assertEqual(caption_y(shot,12.99),1640)
        self.assertEqual(caption_y(shot,13.),570)

    def test_direction_file_is_confined_and_hashed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'references').mkdir();(root/'references/style.md').write_text('Warm steel.')
            (root/'script.md').write_text('## S01 | 4.0 | hydraulics | hydraulics\nThe pump moves oil.\n')
            config={'schema_version':1,'id':'test','title':'Test','template':'garage','direction':'direction.json'}
            (root/'story.json').write_text(json.dumps(config));(root/'direction.json').write_text(json.dumps(self.doc))
            before=load_story(root)
            self.doc['shots']['S01'][0]['scale']=1.4
            (root/'direction.json').write_text(json.dumps(self.doc))
            self.assertNotEqual(before['source_sha256'],load_story(root)['source_sha256'])
            self.assertEqual(len(before['shots'][0]['direction']),3)
            config['direction']='../direction.json';(root/'story.json').write_text(json.dumps(config))
            with self.assertRaises(StoryError):load_story(root)


if __name__=='__main__':unittest.main()
