"""Failure handling and frame/provenance checks for story folder inputs."""
import json
from pathlib import Path
import tempfile
import unittest

from story import load_story, StoryError


class StoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)/'example'
        self.root.mkdir()
        (self.root/'references').mkdir()
        (self.root/'references'/'style.md').write_text('Warm manufactured steel, soft daylight.\n')
        self.config = {'schema_version':1, 'id':'example', 'title':'A pressure story',
                       'template':'hydraulic_lab', 'fps':30}
        self.script = '# A pressure story\n\n## S01 | 2.0 | pressure | hydraulics\nPressure moves the piston.\n\n## S02 | 1.5 | extend | cutaway\nThe load rises.\n'
        self.write()

    def tearDown(self):
        self.temp.cleanup()

    def write(self):
        (self.root/'story.json').write_text(json.dumps(self.config))
        (self.root/'script.md').write_text(self.script)

    def test_whole_frame_plan_has_no_boundary_gaps(self):
        story = load_story(self.root)
        self.assertEqual((story['frames'],story['duration_s']), (105,3.5))
        first, second = story['shots']
        self.assertEqual((first['start_frame'],first['end_frame']), (1,60))
        self.assertEqual((second['start_frame'],second['end_frame']), (61,105))
        self.assertEqual(first['end'],second['start'])
        self.assertEqual(story['audio'],{'mode':'espeak','voice':'en-us','rate':175})

    def test_fractional_frame_duration_rejected(self):
        self.script = self.script.replace('2.0 | pressure','0.05 | pressure')
        self.write()
        with self.assertRaisesRegex(StoryError,'whole frames'):
            load_story(self.root)

    def test_unsupported_action_rejected_before_render(self):
        self.script = self.script.replace('pressure | hydraulics','invent_new_robot | hydraulics')
        self.write()
        with self.assertRaisesRegex(StoryError,'not supported'):
            load_story(self.root)

    def test_camera_typo_rejected(self):
        self.script = self.script.replace('extend | cutaway','extend | orbitfast')
        self.write()
        with self.assertRaisesRegex(StoryError,'unsupported camera'):
            load_story(self.root)

    def test_header_typo_cannot_silently_become_narration(self):
        self.script = self.script.replace('## S02 |','## S02 :')
        self.write()
        with self.assertRaisesRegex(StoryError,'Script line'):
            load_story(self.root)

    def test_each_shot_needs_narration(self):
        self.script = self.script.replace('Pressure moves the piston.','')
        self.write()
        with self.assertRaisesRegex(StoryError,'needs narration'):
            load_story(self.root)

    def test_duplicate_shot_ids_rejected(self):
        self.script = self.script.replace('S02','S01')
        self.write()
        with self.assertRaisesRegex(StoryError,'Duplicate shot'):
            load_story(self.root)

    def test_unknown_json_fields_rejected(self):
        self.config['scrpit']='typo.md'
        self.write()
        with self.assertRaisesRegex(StoryError,'Unknown story.json fields'):
            load_story(self.root)

    def test_duplicate_json_fields_rejected(self):
        (self.root/'story.json').write_text('{"schema_version":1,"schema_version":2}')
        with self.assertRaisesRegex(StoryError,'Duplicate JSON field'):
            load_story(self.root)

    def test_invalid_fps_and_template_values(self):
        for value in (29.97, True, 0, 61):
            with self.subTest(fps=value):
                self.config['fps']=value
                self.write()
                with self.assertRaisesRegex(StoryError,'fps must'):
                    load_story(self.root)
        self.config['fps']=30
        for value in ('unknown',{},None):
            with self.subTest(template=value):
                self.config['template']=value
                self.write()
                with self.assertRaisesRegex(StoryError,'Unsupported template'):
                    load_story(self.root)

    def test_parent_paths_cannot_read_other_story(self):
        outside=Path(self.temp.name)/'elsewhere.md'
        outside.write_text('Not a reference for this folder.')
        self.config['references']=['../elsewhere.md']
        self.write()
        with self.assertRaisesRegex(StoryError,'inside its story folder'):
            load_story(self.root)

    def test_symlink_escape_rejected_during_auto_inventory(self):
        outside=Path(self.temp.name)/'elsewhere.md'
        outside.write_text('Outside reference.')
        (self.root/'references'/'linked.md').symlink_to(outside)
        with self.assertRaisesRegex(StoryError,'outside its story folder'):
            load_story(self.root)

    def test_missing_reference_and_empty_inventory_rejected(self):
        self.config['references']=['references/missing.jpg']
        self.write()
        with self.assertRaisesRegex(StoryError,'file is missing'):
            load_story(self.root)
        del self.config['references']
        (self.root/'references'/'style.md').unlink()
        self.write()
        with self.assertRaisesRegex(StoryError,'at least one file'):
            load_story(self.root)

    def test_reference_change_invalidates_source_fingerprint(self):
        before=load_story(self.root)
        reference=self.root/'references'/'style.md'
        reference.write_text('Changed oak grain and softer light.')
        after=load_story(self.root)
        self.assertNotEqual(before['source_sha256'],after['source_sha256'])
        self.assertNotEqual(before['references'][0]['sha256'],after['references'][0]['sha256'])
        self.assertEqual(before['script_sha256'],after['script_sha256'])

    def test_recorded_audio_and_real_caption_paths(self):
        # The loader validates provenance and paths; audio preparation validates
        # the actual WAV/SRT contents before rendering starts.
        (self.root/'narration.wav').write_bytes(b'RIFFexample')
        (self.root/'captions.srt').write_text('1\n00:00:00,000 --> 00:00:01,000\nPressure\n')
        self.config['audio']={'mode':'file','file':'narration.wav','captions_file':'captions.srt'}
        self.write()
        story=load_story(self.root)
        self.assertEqual(story['audio']['file'],'narration.wav')
        self.assertEqual(story['audio']['captions_file'],'captions.srt')
        before=story['source_sha256']
        (self.root/'narration.wav').write_bytes(b'RIFFchanged')
        self.assertNotEqual(before,load_story(self.root)['source_sha256'])

    def test_native_phone_recording_format_is_accepted(self):
        (self.root/'narration.m4a').write_bytes(b'validated by FFmpeg during audio preparation')
        self.config['audio']={'mode':'file','file':'narration.m4a'}
        self.write()
        self.assertEqual(load_story(self.root)['audio']['file'],'narration.m4a')

    def test_audio_misconfiguration_rejected(self):
        for audio in ({'mode':'file'}, {'mode':'online-api'}, {'mode':'none','file':'unused.wav'},
                      {'rate':'175'}, {'mode':'espeak','unknown':True}):
            with self.subTest(audio=audio):
                self.config['audio']=audio
                self.write()
                with self.assertRaises(StoryError):
                    load_story(self.root)

    def test_committed_examples_compile_as_documented(self):
        repository=Path(__file__).resolve().parent.parent
        garage=load_story(repository/'stories'/'hidden-garage')
        lab=load_story(repository/'stories'/'hydraulic-basics')
        template=load_story(repository/'stories'/'_template')
        self.assertEqual((garage['frames'],garage['duration_s'],len(garage['shots'])),(1530,51.0,12))
        self.assertEqual((garage['shots'][0]['action'],garage['shots'][0]['frames']),('arrive',210))
        self.assertEqual((lab['template'],lab['frames']),('hydraulic_lab',450))
        self.assertEqual(template['template'],'hydraulic_lab')
        self.assertTrue(any(r['path'].endswith('storyboard.jpg') for r in garage['references']))


if __name__=='__main__':
    unittest.main()
