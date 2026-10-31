"""Validate a versioned story folder and compile frame-exact narration beats.

References are inventoried for human look development and provenance. This module
never claims to infer 3D meshes or animation from a reference image or free text.
"""
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re

TEMPLATES = {
    'garage': frozenset({'arrive', 'excavate', 'collapse', 'reinforce', 'load',
                         'hydraulics', 'rain', 'drainage', 'pinch', 'sensors',
                         'conceal', 'payoff'}),
    'hydraulic_lab': frozenset({'pressure', 'extend', 'retract'}),
}
CAMERAS = frozenset({'arrival', 'exterior', 'cutaway', 'hydraulics', 'drainage', 'sensor'})
CONFIG_KEYS = frozenset({'schema_version', 'id', 'title', 'template', 'fps',
                         'script', 'references', 'audio'})
AUDIO_KEYS = frozenset({'mode', 'voice', 'rate', 'file', 'captions_file'})
HEADER = re.compile(r'^##\s+(S\d{2,3})\s*\|\s*([0-9]+(?:\.[0-9]+)?)\s*\|\s*([a-z][a-z0-9_]*)\s*\|\s*([a-z][a-z0-9_]*)\s*$')
SLUG = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')


class StoryError(ValueError):
    """A story cannot be rendered as declared; fail before expensive rendering."""


def _object(value, label, allowed):
    if not isinstance(value, dict):
        raise StoryError(f'{label} must be a JSON object')
    unknown = set(value)-allowed
    if unknown:
        raise StoryError(f'Unknown {label} fields: {", ".join(sorted(unknown))}')
    return value


def _local_file(root, value, label):
    if not isinstance(value, str) or not value.strip():
        raise StoryError(f'{label} must be a nonempty relative file path')
    relative = Path(value)
    if relative.is_absolute() or '\\' in value or '..' in relative.parts or ':' in value:
        raise StoryError(f'{label} must stay inside its story folder: {value!r}')
    path = (root/relative).resolve()
    if not path.is_relative_to(root):
        raise StoryError(f'{label} resolves outside its story folder: {value!r}')
    if not path.is_file():
        raise StoryError(f'{label} file is missing: {value}')
    return path


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_script(text, template, fps):
    """Parse plain narration under ``## ID | seconds | action | camera`` headers."""
    shots = []
    current = None
    lines = []
    cursor = 0
    seen = set()

    def finish():
        nonlocal current, lines, cursor
        if current is None:
            return
        narration = ' '.join(' '.join(lines).split())
        if not narration:
            raise StoryError(f'{current["id"]} needs narration beneath its header')
        current.update(narration=narration, start=cursor/fps,
                       end=(cursor+current['frames'])/fps,
                       start_frame=cursor+1, end_frame=cursor+current['frames'])
        cursor += current['frames']
        shots.append(current)
        current, lines = None, []

    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith('##'):
            match = HEADER.fullmatch(stripped)
            if not match:
                raise StoryError(f'Script line {number}: expected ## S01 | seconds | action | camera')
            finish()
            shot_id, duration_text, action, camera = match.groups()
            if shot_id in seen:
                raise StoryError(f'Duplicate shot id: {shot_id}')
            seen.add(shot_id)
            if action not in TEMPLATES[template]:
                raise StoryError(f'{shot_id}: action {action!r} is not supported by template {template!r}')
            if camera not in CAMERAS:
                raise StoryError(f'{shot_id}: unsupported camera {camera!r}')
            try:
                duration = Decimal(duration_text)
            except InvalidOperation as error:
                raise StoryError(f'{shot_id}: invalid duration') from error
            frames = duration*fps
            if duration <= 0 or frames != frames.to_integral_value():
                raise StoryError(f'{shot_id}: duration must be positive and cover whole frames at {fps} fps')
            current = {'id':shot_id, 'duration_s':float(duration), 'frames':int(frames),
                       'action':action, 'camera':camera}
        elif current is None:
            if stripped and not stripped.startswith('# '):
                raise StoryError(f'Script line {number}: narration must follow a shot header')
        elif stripped:
            if stripped.startswith('#') or '<!--' in stripped:
                raise StoryError(f'Script line {number}: use plain narration, not nested headings/comments')
            lines.append(stripped)
    finish()
    if not shots:
        raise StoryError('script.md needs at least one shot header and narration paragraph')
    return shots


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise StoryError(f'Duplicate JSON field: {key}')
        result[key] = value
    return result


def load_story(directory):
    """Return a serializable plan, rejecting unsupported actions before rendering."""
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        raise StoryError(f'Story folder does not exist: {root}')
    config_path = _local_file(root, 'story.json', 'Configuration')
    try:
        config = json.loads(config_path.read_text(encoding='utf-8'), object_pairs_hook=_unique_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise StoryError(f'Invalid story.json: {error}') from error
    _object(config, 'story.json', CONFIG_KEYS)
    if type(config.get('schema_version')) is not int or config['schema_version'] != 1:
        raise StoryError('story.json schema_version must be integer 1')
    story_id = config.get('id')
    if not isinstance(story_id, str) or not SLUG.fullmatch(story_id):
        raise StoryError('id must be a lowercase hyphenated slug, for example hidden-garage')
    title = config.get('title')
    if not isinstance(title, str) or not title.strip():
        raise StoryError('title must be nonempty text')
    template = config.get('template')
    if not isinstance(template, str) or template not in TEMPLATES:
        raise StoryError(f'Unsupported template {template!r}; choose {", ".join(TEMPLATES)}')
    fps = config.get('fps', 30)
    if type(fps) is not int or not 1 <= fps <= 60:
        raise StoryError('fps must be an integer between 1 and 60')
    script_relative = config.get('script', 'script.md')
    script = _local_file(root, script_relative, 'Script')
    try:
        shots = parse_script(script.read_text(encoding='utf-8'), template, fps)
    except UnicodeDecodeError as error:
        raise StoryError('Script must be UTF-8 text') from error
    audio = _object(config.get('audio', {}), 'audio', AUDIO_KEYS)
    mode = audio.get('mode', 'espeak')
    if mode not in ('espeak', 'file', 'none'):
        raise StoryError('audio.mode must be espeak, file, or none')
    voice = audio.get('voice', 'en-us')
    if not isinstance(voice, str) or not re.fullmatch(r'[A-Za-z0-9_+.-]{1,64}', voice):
        raise StoryError('audio.voice must be an eSpeak voice identifier, for example en-us')
    rate = audio.get('rate', 175)
    if type(rate) is not int or not 80 <= rate <= 450:
        raise StoryError('audio.rate must be an integer between 80 and 450 words per minute')
    normalized_audio = {'mode':mode, 'voice':voice, 'rate':rate}
    additional_sources = []
    if mode == 'file':
        file = _local_file(root, audio.get('file'), 'Narration audio')
        if file.suffix.lower() != '.wav':
            raise StoryError('Narration audio must be a .wav file')
        normalized_audio['file'] = file.relative_to(root).as_posix()
        additional_sources.append(file)
    elif 'file' in audio:
        raise StoryError('audio.file is only valid with audio.mode=file')
    if 'captions_file' in audio:
        captions = _local_file(root, audio['captions_file'], 'Timed captions')
        if captions.suffix.lower() != '.srt':
            raise StoryError('audio.captions_file must be an .srt file')
        normalized_audio['captions_file'] = captions.relative_to(root).as_posix()
        additional_sources.append(captions)
    reference_values = config.get('references')
    if reference_values is None:
        reference_values = sorted(p.relative_to(root).as_posix() for p in (root/'references').rglob('*') if p.is_file())
    if not isinstance(reference_values, list) or not reference_values:
        raise StoryError('Add at least one file under references/ or list references in story.json')
    references = []
    reference_paths = set()
    for value in reference_values:
        path = _local_file(root, value, 'Reference')
        relative = path.relative_to(root).as_posix()
        if relative in reference_paths:
            raise StoryError(f'Duplicate reference file: {relative}')
        reference_paths.add(relative)
        references.append({'path':relative, 'sha256':_sha(path), 'bytes':path.stat().st_size})
    sources = [config_path, script]+[root/r['path'] for r in references]+additional_sources
    digest = hashlib.sha256()
    for path in sorted(set(sources)):
        digest.update(path.relative_to(root).as_posix().encode('utf-8'))
        digest.update(b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
    frames = sum(s['frames'] for s in shots)
    return {'schema_version':1, 'id':story_id, 'title':title.strip(), 'template':template,
            'fps':fps, 'root':str(root), 'script':script.relative_to(root).as_posix(),
            'script_sha256':_sha(script), 'source_sha256':digest.hexdigest(),
            'shots':shots, 'frames':frames, 'duration_s':frames/fps,
            'references':references, 'audio':normalized_audio}
