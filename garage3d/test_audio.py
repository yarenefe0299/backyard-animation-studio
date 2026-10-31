"""Exercise actual audio lengths, recording support, subtitle safety and synthesis."""
from array import array
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import wave

from audio import SAMPLE_RATE, atempo_chain, phrase_groups, prepare_audio, read_srt


def example(mode='none', duration=2.):
    return {'id':'test','title':'Audio test','duration_s':duration,'fps':30,
            'audio':{'mode':mode,'voice':'en-us','rate':175},
            'shots':[{'id':'S01','start':0.,'end':duration,'duration_s':duration,
                      'action':'extend','camera':'hydraulics',
                      'narration':'Oil pressure pushes the piston upward.'}]}


def write_recording(path, duration):
    samples = array('h',(round(6000*math.sin(2*math.pi*180*i/SAMPLE_RATE)) for i in range(round(duration*SAMPLE_RATE))))
    with wave.open(str(path),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(SAMPLE_RATE)
        out.writeframes(samples.tobytes())


class AudioTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg not installed')
    def test_caption_zone_changes_even_when_a_phrase_spans_a_cut(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);story=example()
            story['shots'][0]['narration']='The pressure pushes.'
            story['shots'][0]['direction']=[{'at':0,'view':'pump','move':0,'scale':1.6,'end_scale':1.6},
                                            {'at':1,'view':'lift','move':0,'scale':7.8,'end_scale':7.8}]
            result=prepare_audio(story,root,root/'output')
            captions=Path(result['captions_ass']).read_text()
            self.assertIn('pos(540,1640)',captions)
            self.assertIn('pos(540,570)',captions)
            cues=read_srt(result['captions_srt'],2)
            self.assertTrue(all(cue['end']<=1 or cue['start']>=1 for cue in cues))

    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg not installed')
    def test_mechanism_excerpt_uses_later_recording_and_rebases_srt(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_recording(root/'voice.wav',6.)
            with wave.open(str(root/'voice.wav'),'rb') as source:
                values=array('h',source.readframes(source.getnframes()))
            values[:3*SAMPLE_RATE]=array('h',[0])*(3*SAMPLE_RATE)
            with wave.open(str(root/'voice.wav'),'wb') as out:
                out.setparams((1,2,SAMPLE_RATE,0,'NONE','not compressed'));out.writeframes(values.tobytes())
            (root/'words.srt').write_text('1\n00:00:00,500 --> 00:00:01,000\nOpening words\n\n2\n00:00:04,000 --> 00:00:05,000\nLater words\n')
            story=example('file');story.update(source_duration_s=6.,source_start_s=3.5)
            story['audio'].update(file='voice.wav',captions_file='words.srt')
            result=prepare_audio(story,root,root/'output')
            cues=read_srt(result['captions_srt'],2)
            self.assertEqual([cue['text'] for cue in cues],['Later words'])
            self.assertAlmostEqual(cues[0]['start'],.1+4/(6/5.8)-3.5,places=3)
            with wave.open(result['narration']) as audio:
                samples=array('h',audio.readframes(audio.getnframes()))
                self.assertEqual(len(samples),2*SAMPLE_RATE)
                self.assertGreater(max(abs(v) for v in samples[:SAMPLE_RATE]),1000)

    def test_tempo_chain_preserves_large_and_small_factors(self):
        for factor in [.1,.5,1,2,9]:
            stages=[float(part.split('=')[1]) for part in atempo_chain(factor).split(',')]
            self.assertTrue(all(.5 <= stage <= 2 for stage in stages))
            self.assertAlmostEqual(math.prod(stages),factor,places=8)
        for value in [0,-1,float('inf')]:
            with self.assertRaises(ValueError):atempo_chain(value)

    def test_phrase_groups_are_short_without_orphaned_end(self):
        groups=phrase_groups('One two three four five six seven')
        self.assertEqual(' '.join(groups),'One two three four five six seven')
        self.assertTrue(all(2 <= len(group.split()) <= 4 for group in groups))

    def test_supplied_srt_rejects_outside_or_overlapping_cues(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'captions.srt'
            p.write_text('1\n00:00:00,000 --> 00:00:03,000\nOutside\n')
            with self.assertRaises(ValueError):read_srt(p,2)
            p.write_text('1\n00:00:00,000 --> 00:00:01,500\nFirst\n\n2\n00:00:01,000 --> 00:00:02,000\nOverlap\n')
            with self.assertRaises(ValueError):read_srt(p,2)

    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg not installed')
    def test_phone_m4a_is_decoded_and_fitted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_recording(root/'source.wav',2.5)
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(root/'source.wav'),'-c:a','aac',str(root/'phone.m4a')],check=True)
            story=example('file');story['audio']['file']='phone.m4a'
            result=prepare_audio(story,root,root/'output')
            with wave.open(result['narration']) as audio:
                values=array('h',audio.readframes(audio.getnframes()))
                self.assertEqual(len(values),2*SAMPLE_RATE)
                self.assertGreater(max(abs(v) for v in values),1000)

    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg not installed')
    def test_silent_narration_keeps_original_foley_and_exact_duration(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);result=prepare_audio(example(),root,root/'output')
            with wave.open(result['narration']) as source:
                self.assertEqual(source.getnframes(),2*SAMPLE_RATE)
                self.assertEqual(set(array('h',source.readframes(source.getnframes()))),{0})
            with wave.open(result['soundtrack']) as source:
                samples=array('h',source.readframes(source.getnframes()))
                self.assertEqual(len(samples),2*SAMPLE_RATE)
                self.assertGreater(max(samples),0)
                self.assertLessEqual(max(abs(v) for v in samples),32113)
            report=json.loads(Path(result['report']).read_text())
            self.assertEqual(report['voice_source'],'no narration')
            self.assertIn('not word-level forced alignment',report['caption_timing'])

    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg not installed')
    def test_recording_is_fitted_and_supplied_caption_times_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_recording(root/'voice.wav',3.5)
            (root/'words.srt').write_text('1\n00:00:00,500 --> 00:00:01,500\nOriginal recording\n')
            story=example('file');story['audio'].update(file='voice.wav',captions_file='words.srt')
            result=prepare_audio(story,root,root/'output')
            with wave.open(result['narration']) as source:
                self.assertEqual(source.getnframes(),2*SAMPLE_RATE)
            cues=read_srt(result['captions_srt'],2)
            self.assertAlmostEqual(cues[0]['start'],.1+.5/(3.5/1.8),places=3)
            self.assertAlmostEqual(cues[0]['end'],.1+1.5/(3.5/1.8),places=3)
            report=json.loads(Path(result['report']).read_text())
            self.assertEqual(report['caption_timing'],'supplied SRT cues retimed with recording and clipped to scope')
            self.assertEqual(report['voice_source'],'user-provided narration recording')

    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg not installed')
    def test_opening_trims_full_recording_and_later_captions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_recording(root/'voice.wav',6.)
            (root/'words.srt').write_text('1\n00:00:00,500 --> 00:00:01,000\nOpening words\n\n2\n00:00:04,000 --> 00:00:05,000\nLater words\n')
            story=example('file');story['source_duration_s']=6.
            story['audio'].update(file='voice.wav',captions_file='words.srt')
            result=prepare_audio(story,root,root/'output')
            report=json.loads(Path(result['report']).read_text())
            self.assertAlmostEqual(report['recording_timing']['tempo_factor'],6/5.8)
            cues=read_srt(result['captions_srt'],2)
            self.assertEqual(len(cues),1)
            self.assertEqual(cues[0]['text'],'Opening words')
            with wave.open(result['soundtrack']) as source:
                self.assertEqual(source.getnframes(),2*SAMPLE_RATE)

    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg not installed')
    def test_external_audio_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            story=example('file');story['audio']['file']='../voice.wav'
            with self.assertRaises(ValueError):prepare_audio(story,Path(d),Path(d)/'output')

    @unittest.skipUnless(shutil.which('ffmpeg'),'FFmpeg not installed')
    def test_caption_text_cannot_inject_ass_tags_and_libass_accepts_output(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);story=example()
            story['shots'][0]['narration']='Literal {\\bord0} and \\N remain text.'
            result=prepare_audio(story,root,root/'output')
            content=Path(result['captions_ass']).read_text()
            self.assertNotIn('{\\bord0}',content)
            self.assertIn('｛＼bord0｝',content)
            target=root/'output'/'caption-check.mp4'
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i','color=c=gray:s=136x240:d=0.1',
                            '-vf','ass=captions.ass','-c:v','libx264','-pix_fmt','yuv420p',str(target)],cwd=root/'output',check=True)
            self.assertGreater(target.stat().st_size,100)

    @unittest.skipUnless(shutil.which('ffmpeg') and (shutil.which('espeak-ng') or shutil.which('espeak')),'eSpeak/FFmpeg not installed')
    def test_real_offline_voice_is_bounded_by_each_shot(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);story=example('espeak',3.)
            first=story['shots'][0];first.update(end=1.5,duration_s=1.5)
            second={**first,'id':'S02','start':1.5,'end':3.,'action':'retract'}
            story['shots'].append(second)
            result=prepare_audio(story,root,root/'output')
            with wave.open(result['narration']) as source:
                samples=array('h',source.readframes(source.getnframes()))
                self.assertEqual(len(samples),3*SAMPLE_RATE)
                self.assertGreater(max(abs(v) for v in samples),1000)
            report=json.loads(Path(result['report']).read_text())
            self.assertEqual(report['voice_source'],'offline eSpeak synthetic draft voice')
            for source,span in zip(story['shots'],report['shots']):
                self.assertGreaterEqual(span['spoken_start'],source['start'])
                self.assertLessEqual(span['spoken_end'],source['end'])
                self.assertGreater(span['tempo_factor'],1)


if __name__=='__main__':unittest.main()
