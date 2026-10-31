"""Test real narration/caption assembly and frame-plan boundaries."""
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import zlib
from pipeline import make_plan,assemble
from audio import prepare_audio


def png(path,color):
    def chunk(kind,payload):
        return struct.pack('>I',len(payload))+kind+payload+struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff)
    raw=b''.join(b'\0'+bytes(color)*32 for _ in range(64))
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',32,64,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))


class PipelineTests(unittest.TestCase):
    def test_opening_and_full_plans_cover_exact_frames(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(__file__).resolve().parent.parent/'stories/hidden-garage'
            for scope,n in [('opening',180),('mechanism',210),('full',1530)]:
                p=make_plan(root,Path(d)/scope,scope=scope)
                actual=[f for c in p['matrix']['include'] for f in range(c['from'],c['to']+1)]
                self.assertEqual(actual,list(range(1,n+1)))
                self.assertEqual(p['source_duration_s'],51)
                if scope=='mechanism':
                    self.assertEqual(p['source_start_s'],19.7)
                    self.assertEqual((p['shots'][0]['id'],p['shots'][0]['start']),('S06',0))
    def test_changed_plan_rejects_existing_frames(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(__file__).resolve().parent.parent/'stories/hidden-garage'
            make_plan(root,d)
            frames=Path(d)/'frames';frames.mkdir();png(frames/'frame_0001.png',(1,2,3))
            with self.assertRaisesRegex(ValueError,'different plan'):make_plan(root,d,scope='full')
    def test_story_folder_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'inside'):make_plan(d,d)
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
    def test_actual_captioned_h264_aac_roundtrip_and_missing_frame_guard(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d);frames=output/'frames';frames.mkdir()
            plan={'id':'test','scope':'full','source_sha256':'test-source','frames':6,'fps':30,'duration_s':.2,'resolution':[32,64],
                  'audio':{'mode':'none'},'shots':[{'id':'S01','start':0,'end':.2,'duration_s':.2,'narration':'A tiny test.','action':'pressure','start_frame':1,'end_frame':6}]}
            (output/'plan.json').write_text(json.dumps(plan))
            prepare_audio(plan,output,output)
            for i in range(1,7):png(frames/f'frame_{i:04d}.png',(i*30,80,100))
            report=assemble(output,denoise=False)
            self.assertEqual(report['video_stream']['nb_read_frames'],'6')
            self.assertEqual(report['audio_stream']['codec_name'],'aac')
            self.assertTrue((output/'contact-sheet.png').is_file())
            (frames/'frame_0006.png').unlink()
            with self.assertRaisesRegex(ValueError,'Incomplete'):assemble(output,denoise=False)
            self.assertFalse((output/'story.mp4').exists())

if __name__=='__main__':unittest.main()
