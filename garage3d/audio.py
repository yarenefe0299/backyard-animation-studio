"""Offline narration, honest phrase timing, captions and original procedural SFX.

No voice cloning or network synthesis. eSpeak NG is a draft voice; supply a WAV
and optional SRT in the story folder for a polished performance.
"""
from array import array
from pathlib import Path
import argparse
import hashlib
import json
import math
import random
import re
import shutil
import subprocess
import tempfile
import wave

SAMPLE_RATE = 48000


def _run(command):
    result = subprocess.run([str(p) for p in command], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if result.returncode:
        detail = result.stderr.decode('utf-8',errors='replace').strip()[-2000:]
        raise RuntimeError(f'{Path(command[0]).name} failed ({result.returncode}): {detail}')


def _relative_file(root, name):
    root = Path(root).resolve()
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Audio/caption inputs must stay inside the story folder')
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f'Missing or external story input: {name}')
    return path


def _read_wav(path):
    with wave.open(str(path), 'rb') as source:
        if source.getnchannels() != 1 or source.getsampwidth() != 2 or source.getframerate() != SAMPLE_RATE:
            raise ValueError('Internal audio must be mono PCM16 at 48000 Hz')
        samples = array('h', source.readframes(source.getnframes()))
    return samples


def _duration(path):
    with wave.open(str(path), 'rb') as source:
        return source.getnframes() / source.getframerate()


def _write_wav(path, samples):
    with wave.open(str(path), 'wb') as destination:
        destination.setnchannels(1)
        destination.setsampwidth(2)
        destination.setframerate(SAMPLE_RATE)
        destination.writeframes(samples.tobytes())


def atempo_chain(factor):
    """Keep every atempo stage within FFmpeg's high-quality 0.5..2 range."""
    if not math.isfinite(factor) or factor <= 0:
        raise ValueError('Tempo must be positive and finite')
    factors = []
    while factor > 2:
        factors.append(2.)
        factor /= 2
    while factor < .5:
        factors.append(.5)
        factor *= 2
    factors.append(factor)
    return ','.join(f'atempo={value:.10f}' for value in factors)


def _convert(source, destination, available, allow_slowdown=False):
    original = _duration(source)
    if original <= 0 or available <= 0:
        raise ValueError('Narration and shot windows must have positive duration')
    tempo = original / available if allow_slowdown else max(1., original / available)
    _run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', source,
          '-vn', '-af', atempo_chain(tempo), '-ar', str(SAMPLE_RATE), '-ac', '1',
          '-c:a', 'pcm_s16le', destination])
    samples = _read_wav(destination)
    # atempo's filter window can leave a tiny tail; never cross a shot boundary.
    return samples[:round(available*SAMPLE_RATE)], tempo


def phrase_groups(text):
    """Readable short captions; avoid a stranded one-word final group."""
    words = text.split()
    groups = []
    while words:
        take = 4 if len(words) == 4 else min(3, len(words))
        groups.append(' '.join(words[:take]))
        words = words[take:]
    return groups


def _timestamp(seconds, separator=',', digits=3):
    units = 10**digits
    total = max(0, round(seconds*units))
    hours, total = divmod(total, 3600*units)
    minutes, total = divmod(total, 60*units)
    seconds, fraction = divmod(total, units)
    return f'{hours:02}:{minutes:02}:{seconds:02}{separator}{fraction:0{digits}}'


def _ass_text(text):
    # User text must not inject ASS override tags or linebreak escapes.
    return text.replace('\\', '＼').replace('{', '｛').replace('}', '｝').replace('\n', ' ').replace('\r', ' ')


def read_srt(path, duration):
    result = []
    content = Path(path).read_text(encoding='utf-8-sig').strip()
    stamp = r'(\d+):(\d{2}):(\d{2})[,.](\d{3})'
    def seconds(parts):
        h,m,s,ms = map(int, parts)
        if m >= 60 or s >= 60:
            raise ValueError('Invalid SRT time')
        return h*3600+m*60+s+ms/1000
    for block in re.split(r'\n\s*\n', content):
        lines = block.strip().splitlines()
        if not lines:
            continue
        if lines[0].strip().isdigit():
            lines = lines[1:]
        if len(lines) < 2:
            raise ValueError('SRT cues need a time range and text')
        match = re.fullmatch(stamp+r'\s*-->\s*'+stamp, lines[0].strip())
        if not match:
            raise ValueError('Invalid SRT timestamp')
        start, end = seconds(match.groups()[:4]), seconds(match.groups()[4:])
        if not 0 <= start < end <= duration+.001:
            raise ValueError('SRT cue is outside the story duration')
        if result and start < result[-1]['end']-.001:
            raise ValueError('SRT cues must not overlap or run backwards')
        result.append({'start':start, 'end':end, 'text':' '.join(lines[1:])})
    if not result:
        raise ValueError('The supplied SRT has no cues')
    return result


def write_captions(cues, output, title):
    output = Path(output)
    srt = output/'captions.srt'
    ass = output/'captions.ass'
    srt.write_text('\n\n'.join(f"{i}\n{_timestamp(c['start'])} --> {_timestamp(c['end'])}\n{c['text']}" for i,c in enumerate(cues, 1))+'\n', encoding='utf-8')
    header = f'''[Script Info]
Title: {_ass_text(title)}
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Explainer,DejaVu Sans,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,0,2,70,70,320,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    events = '\n'.join('Dialogue: 0,'+_timestamp(c['start'],'.',2)+','+_timestamp(c['end'],'.',2)+',Explainer,,0,0,0,,{\\pos(540,'+str(c.get('caption_y',1500))+')}'+_ass_text(c['text']) for c in cues)
    ass.write_text(header+events+'\n', encoding='utf-8')
    return srt, ass


def _estimated_cues(shots):
    cues = []
    for shot in shots:
        groups = phrase_groups(shot['narration'])
        if not groups:
            continue
        weights = [max(1, len(g)) for g in groups]
        total = sum(weights)
        cursor = shot['spoken_start']
        available = shot['spoken_end']-cursor
        for text, weight in zip(groups, weights):
            end = cursor+available*weight/total
            cues.append({'start':cursor, 'end':end, 'text':text})
            cursor = end
    return cues


def _soundtrack(narration, shots, duration):
    """Freshly synthesized Foley. A fixed seed makes rerenders reproducible."""
    total = round(duration*SAMPLE_RATE)
    effects = array('f', [0])*total
    for shot in shots:
        action = shot['action']
        start = round(shot['start']*SAMPLE_RATE)
        count = min(total-start, round(shot['duration_s']*SAMPLE_RATE))
        seed = int.from_bytes(hashlib.sha256((shot['id']+action).encode()).digest()[:4],'big')
        rng = random.Random(seed)
        low = 0.
        has_voice = any(narration[start:start+count])
        speech_start = shot.get('spoken_start',shot['start'])-shot['start']
        speech_end = shot.get('spoken_end',shot['end'])-shot['start']
        for j in range(count):
            t = j/SAMPLE_RATE
            progress = j/max(1,count-1)
            envelope = min(1, t/.12, (count-j)/(.15*SAMPLE_RATE))
            noise = rng.uniform(-1,1)
            low = .94*low+.06*noise
            if action == 'arrive':
                engine = .085*math.sin(2*math.pi*(85*t+25*t*t))+.04*low
                hydraulic = .065*math.sin(2*math.pi*88*t)+.025*low
                blend = max(0,min(1,(progress-.5)/.1))
                value = engine*(1-blend)+hydraulic*blend
            elif action in {'extend','retract','hydraulics','conceal','payoff','load','pressure'}:
                value = .075*math.sin(2*math.pi*83*t)+.024*math.sin(2*math.pi*169*t)+.045*low
            elif action in {'rain','drainage'}:
                value = .17*low+.023*math.sin(2*math.pi*(420*t+3*math.sin(7*t)))
            elif action in {'excavate','collapse'}:
                value = .21*low+.075*noise*(math.sin(23*t)**12)
            elif action == 'reinforce':
                beat = t % .75
                value = .16*math.exp(-beat*22)*math.sin(2*math.pi*920*beat)+.045*low
            elif action in {'pinch','sensors'}:
                beat = t % .65
                value = .065*math.sin(2*math.pi*840*t)*math.sin(math.pi*beat/.12)**2 if beat < .12 else 0
            else:
                value = 0.
            # Duck Foley beneath actual speech samples; no prerecorded SFX assets.
            speech_envelope = max(0,min(1,(t-speech_start+.08)/.08,(speech_end+.12-t)/.12)) if has_voice else 0
            duck = .85-.45*speech_envelope
            effects[start+j] += value*envelope*duck
    mixed = array('f', (voice/32768*.94+effect for voice,effect in zip(narration,effects)))
    peak = max((abs(x) for x in mixed),default=0)
    gain = min(1., .98/peak) if peak else 1.
    return array('h',(round(max(-1,min(1,x*gain))*32767) for x in mixed)), peak, gain


def prepare_audio(story, story_dir, output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    root = Path(story_dir).resolve()
    duration = float(story['duration_s'])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Story duration must be positive')
    source_duration = float(story.get('source_duration_s', duration))
    if not math.isfinite(source_duration) or source_duration < duration:
        raise ValueError('Source duration must cover the requested scope')
    recording_timing = None
    total = round(duration*SAMPLE_RATE)
    narration = array('h', [0])*total
    audio = story.get('audio', {})
    mode = audio.get('mode','espeak')
    if mode not in {'espeak','file','none'}:
        raise ValueError('Unknown narration mode')
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg is required for audio preparation')
    executable = shutil.which('espeak-ng') or shutil.which('espeak')
    if mode == 'espeak' and not executable:
        raise RuntimeError('Install espeak-ng, or supply audio.mode=file with your narration WAV')
    voice = audio.get('voice','en-us')
    rate = int(audio.get('rate',175))
    if not re.fullmatch(r'[A-Za-z0-9_+.-]+', voice) or not 80 <= rate <= 450:
        raise ValueError('Invalid eSpeak voice or rate')
    spans = []
    with tempfile.TemporaryDirectory(prefix='story-audio-') as temporary:
        temporary = Path(temporary)
        if mode == 'file':
            source = _relative_file(root, audio.get('file',''))
            normalized = temporary/'recording.wav'
            _run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',source,'-vn','-ar',str(SAMPLE_RATE),'-ac','1','-c:a','pcm_s16le',normalized])
            recording_duration = _duration(normalized)
            available = max(.01, source_duration-.2)
            samples, tempo = _convert(normalized,temporary/'fitted.wav',available,allow_slowdown=True)
            offset = min(round(.1*SAMPLE_RATE),total)
            recording_timing = {'source_duration':recording_duration, 'tempo_factor':tempo, 'leading_seconds':offset/SAMPLE_RATE}
            narration[offset:offset+min(len(samples),total-offset)] = samples[:total-offset]
            for shot in story['shots']:
                spans.append({**shot,'spoken_start':shot['start']+.1,'spoken_end':max(shot['start']+.11,shot['end']-.1),'tempo_factor':tempo})
        else:
            for number,shot in enumerate(story['shots']):
                start,end = float(shot['start']),float(shot['end'])
                padding = min(.1,(end-start)*.1)
                offset = round((start+padding)*SAMPLE_RATE)
                available = max(.01,end-start-2*padding)
                text = shot['narration'].strip()
                if mode == 'espeak' and text:
                    text_path = temporary/f'{number}.txt'
                    raw = temporary/f'{number}-raw.wav'
                    fitted = temporary/f'{number}-fit.wav'
                    text_path.write_text(text,encoding='utf-8')
                    _run([executable,'-v',voice,'-s',str(rate),'-w',raw,'-f',text_path])
                    samples,tempo = _convert(raw,fitted,available)
                    count = min(len(samples),max(0,total-offset))
                    narration[offset:offset+count] = samples[:count]
                    spoken_end = (offset+count)/SAMPLE_RATE
                else:
                    tempo = 1.
                    spoken_end = end-padding
                spans.append({**shot,'spoken_start':start+padding,'spoken_end':spoken_end,'tempo_factor':round(tempo,5)})
    narration_path = output/'narration.wav'
    _write_wav(narration_path,narration)
    supplied_cues = audio.get('captions_file')
    if supplied_cues:
        cue_duration = recording_timing['source_duration'] if recording_timing else source_duration
        cues = read_srt(_relative_file(root,supplied_cues),cue_duration)
        if recording_timing:
            for cue in cues:
                cue['start'] = recording_timing['leading_seconds']+cue['start']/recording_timing['tempo_factor']
                cue['end'] = recording_timing['leading_seconds']+cue['end']/recording_timing['tempo_factor']
        cues = [{**cue,'start':max(0,cue['start']),'end':min(duration,cue['end'])} for cue in cues if cue['start'] < duration and cue['end'] > 0]
    else:
        cues = _estimated_cues(spans)
    # Close-up mechanisms occupy the lower picture. Put their captions on the
    # quiet upper wall; exterior/sensor shots keep the reference's lower zone.
    for cue in cues:
        shot=next((s for s in story['shots'] if s['start'] <= cue['start'] < s['end']),story['shots'][-1])
        cue['caption_y']=650 if shot.get('camera') in {'hydraulics','cutaway'} else 1500
    srt,ass = write_captions(cues,output,story.get('title',story.get('id','Explainer')))
    soundtrack,peak,gain = _soundtrack(narration,spans,duration)
    soundtrack_path = output/'soundtrack.wav'
    _write_wav(soundtrack_path,soundtrack)
    report_path = output/'audio_report.json'
    report = {
        'status':'prepared_and_verified','duration_seconds':duration,'sample_rate':SAMPLE_RATE,
        'channels':1,'voice_source':{'espeak':'offline eSpeak synthetic draft voice','file':'user-provided narration recording','none':'no narration'}[mode],
        'voice':voice if mode=='espeak' else None,'rate_wpm':rate if mode=='espeak' else None,
        'caption_timing':('supplied SRT cues retimed with recording and clipped to scope' if recording_timing else 'supplied SRT cues clipped to scope') if supplied_cues else 'estimated phrase timings within speech spans; not word-level forced alignment',
        'recording_timing':recording_timing, 'source_duration_seconds':source_duration,
        'caption_count':len(cues),'shots':[{'id':s['id'],'spoken_start':s['spoken_start'],'spoken_end':s['spoken_end'],'tempo_factor':s['tempo_factor']} for s in spans],
        'sfx_source':'original deterministic procedural Foley; no external audio assets',
        'pre_normalization_peak':round(peak,6),'normalization_gain':round(gain,6),
        'outputs':['narration.wav','soundtrack.wav','captions.ass','captions.srt'],
    }
    assert len(narration)==len(soundtrack)==total
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    return {'narration':str(narration_path),'soundtrack':str(soundtrack_path),
            'captions_ass':str(ass),'captions_srt':str(srt),'report':str(report_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('story',type=Path)
    parser.add_argument('--output',type=Path,default=Path('garage3d/output/audio'))
    args = parser.parse_args()
    from story import load_story
    print(json.dumps(prepare_audio(load_story(args.story),args.story,args.output),indent=2))


if __name__ == '__main__':
    main()
