#!/usr/bin/env python3
"""Offline CPU Open Image Denoise for Blender PNGs, independent of Blender's build.

Install the pinned official Linux binary once, then process images locally. No
image data leaves the runner. Raw frames remain separate from filtered frames.
Color-only LDR filtering cannot use surface normals/albedo or temporal history.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import tarfile
import tempfile
import time
import urllib.request

OIDN_VERSION = '2.3.3'
OIDN_ARCHIVE = 'oidn-2.3.3.x86_64.linux.tar.gz'
OIDN_SHA256 = '3c385230d9e6f63527ba72f2229594dbac5051674219d72e0044b5d0b841796f'
OIDN_URL = f'https://github.com/RenderKit/oidn/releases/download/v{OIDN_VERSION}/{OIDN_ARCHIVE}'
OIDN_LICENSE = 'Apache-2.0; bundled dependency notices remain in upstream doc/'
DEFAULT_ROOT = Path(tempfile.gettempdir()) / 'garage3d-oidn' / OIDN_VERSION
ROOT_FOLDER = f'oidn-{OIDN_VERSION}.x86_64.linux'


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def png_dimensions(path):
    with Path(path).open('rb') as source:
        header = source.read(24)
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError(f'Expected an RGB Blender PNG: {path}')
    size = struct.unpack('>II', header[16:24])
    if not all(size):
        raise ValueError(f'Invalid PNG dimensions: {path}')
    return size


def verify_archive(path):
    actual = sha256(path)
    if actual != OIDN_SHA256:
        raise ValueError(f'OIDN archive SHA-256 mismatch: {actual}; expected {OIDN_SHA256}')


def _safe_extract(archive, destination):
    root = Path(destination).resolve()
    with tarfile.open(archive, 'r:gz') as source:
        for member in source.getmembers():
            target = root / member.name
            if member.name.startswith('/') or '..' in Path(member.name).parts or not target.resolve().is_relative_to(root):
                raise ValueError('Unsafe OIDN archive member')
            if member.issym():
                if not (target.parent / member.linkname).resolve().is_relative_to(root):
                    raise ValueError('Unsafe OIDN archive symlink')
            if member.islnk() and not (root / member.linkname).resolve().is_relative_to(root):
                raise ValueError('Unsafe OIDN archive hard link')
        # Only a SHA-256-verified official archive is accepted by the caller.
        source.extractall(root, filter='data')


def executable_path(directory=None):
    root = Path(directory or os.environ.get('GARAGE_OIDN_ROOT') or DEFAULT_ROOT).resolve()
    executable = root / ROOT_FOLDER / 'bin' / 'oidnDenoise'
    marker = root / 'installation.json'
    if not executable.is_file() or not marker.is_file():
        raise RuntimeError(f'OIDN is not installed at {root}; run denoise.py install --directory {root}')
    record = json.loads(marker.read_text())
    if record.get('archive_sha256') != OIDN_SHA256 or record.get('version') != OIDN_VERSION:
        raise RuntimeError('OIDN installation marker does not match the pinned release')
    return executable


def install_oidn(directory=None, archive_path=None):
    """Explicit setup step. HTTPS download, SHA-256 verification, safe extraction."""
    if platform.system() != 'Linux' or platform.machine().lower() not in ('x86_64', 'amd64'):
        raise RuntimeError('Pinned OIDN installer supports Linux x86_64 runners only')
    root = Path(directory or os.environ.get('GARAGE_OIDN_ROOT') or DEFAULT_ROOT).resolve()
    try:
        return executable_path(root)
    except RuntimeError:
        pass
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='garage-oidn-install-') as scratch:
        archive = Path(archive_path) if archive_path else Path(scratch) / OIDN_ARCHIVE
        if not archive_path:
            with urllib.request.urlopen(OIDN_URL, timeout=60) as response, archive.open('wb') as destination:
                shutil.copyfileobj(response, destination)
        verify_archive(archive)
        _safe_extract(archive, root)
    record = {'engine': 'Intel Open Image Denoise', 'version': OIDN_VERSION,
              'archive_sha256': OIDN_SHA256, 'source_url': OIDN_URL,
              'license': OIDN_LICENSE, 'device': 'CPU'}
    (root / 'installation.json').write_text(json.dumps(record, indent=2) + '\n')
    return executable_path(root)


def denoise_image(source, destination, executable=None, threads=2):
    """Filter one sRGB PNG using real OIDN; no blur fallback and no raw overwrite."""
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination:
        raise ValueError('Denoised output must differ from its preserved raw input')
    if threads < 1:
        raise ValueError('Thread count must be positive')
    width, height = png_dimensions(source)
    program = Path(executable) if executable else executable_path()
    if not program.is_file():
        raise RuntimeError(f'OIDN executable does not exist: {program}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # A failed rerun cannot leave an old success-shaped derivative behind.
    destination.unlink(missing_ok=True)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='garage-oidn-frame-', dir=destination.parent) as scratch:
        scratch = Path(scratch)
        input_pfm, output_pfm, output_png = scratch/'input.pfm', scratch/'output.pfm', scratch/'result.png'
        common = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-threads', '1']
        # FFmpeg may choose big-endian PFM by default; OIDN accepts little-endian.
        subprocess.run(common + ['-i', str(source), '-frames:v', '1', '-threads', '1',
                                 '-pix_fmt', 'gbrpf32le', str(input_pfm)], check=True)
        subprocess.run([str(program), '--device', 'cpu', '--filter', 'RT', '--ldr', str(input_pfm),
                        '--srgb', '--threads', str(threads), '--quality', 'high',
                        '--maxmem', '1024', '--verbose', '0', '--output', str(output_pfm)], check=True)
        subprocess.run(common + ['-i', str(output_pfm), '-frames:v', '1', '-threads', '1',
                                 '-pix_fmt', 'rgb24', str(output_png)], check=True)
        if png_dimensions(output_png) != (width, height):
            raise ValueError('OIDN conversion changed the frame dimensions')
        output_png.replace(destination)
    return {'status': 'denoised_and_verified', 'engine': 'Intel Open Image Denoise',
            'version': OIDN_VERSION, 'device': 'CPU', 'input': str(source), 'output': str(destination),
            'resolution': [width, height], 'source_sha256': sha256(source),
            'output_sha256': sha256(destination), 'seconds': round(time.monotonic()-started, 4),
            'input_mode': 'sRGB LDR; color-only', 'auxiliary_passes': False,
            'temporal_filtering': False, 'raw_input_preserved': True}


def denoise_frames(input_dir, output_dir, executable=None, threads=2, pattern='frame_*.png'):
    """Denoise a chunk or full sequence, preserving names and original frames."""
    source, destination = Path(input_dir).resolve(), Path(output_dir).resolve()
    if source == destination:
        raise ValueError('Raw and denoised frame folders must differ')
    frames = sorted(source.glob(pattern))
    if not frames:
        raise ValueError(f'No frames matching {pattern} in {source}')
    expected = {p.name for p in frames}
    stale = {p.name for p in destination.glob(pattern)} - expected
    if stale:
        raise ValueError(f'Stale denoised frames in destination: {sorted(stale)[:8]}')
    program = Path(executable) if executable else executable_path()
    destination.mkdir(parents=True, exist_ok=True)
    report_path = destination/'denoise_report.json'
    report = {'status': 'running', 'engine': 'Intel Open Image Denoise', 'version': OIDN_VERSION,
              'archive_sha256': OIDN_SHA256, 'input_mode': 'sRGB LDR; color-only',
              'auxiliary_passes': False, 'temporal_filtering': False,
              'raw_input_preserved': True, 'source_frames': len(frames), 'completed_frames': [],
              'raw_directory': str(source), 'output_directory': str(destination)}
    def write_report():
        report_path.write_text(json.dumps(report, indent=2)+'\n')
    write_report()
    try:
        for frame in frames:
            detail = denoise_image(frame, destination/frame.name, program, threads)
            report['completed_frames'].append({'name': frame.name, 'source_sha256': detail['source_sha256'],
                                               'output_sha256': detail['output_sha256'],
                                               'seconds': detail['seconds']})
            write_report()
        report['status'] = 'denoised_and_verified'
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = str(error)
        raise
    finally:
        write_report()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    setup = commands.add_parser('install')
    setup.add_argument('--directory', type=Path, default=DEFAULT_ROOT)
    setup.add_argument('--archive', type=Path)
    image = commands.add_parser('image')
    image.add_argument('--input', type=Path, required=True)
    image.add_argument('--output', type=Path, required=True)
    image.add_argument('--oidn-root', type=Path, default=DEFAULT_ROOT)
    image.add_argument('--threads', type=int, default=2)
    sequence = commands.add_parser('frames')
    sequence.add_argument('--input', type=Path, required=True)
    sequence.add_argument('--output', type=Path, required=True)
    sequence.add_argument('--oidn-root', type=Path, default=DEFAULT_ROOT)
    sequence.add_argument('--threads', type=int, default=2)
    sequence.add_argument('--pattern', default='frame_*.png')
    arguments = parser.parse_args()
    if arguments.command == 'install':
        print(install_oidn(arguments.directory, arguments.archive))
    elif arguments.command == 'image':
        print(json.dumps(denoise_image(arguments.input, arguments.output,
                                       executable_path(arguments.oidn_root), arguments.threads), indent=2))
    else:
        report = denoise_frames(arguments.input, arguments.output,
                                executable_path(arguments.oidn_root), arguments.threads, arguments.pattern)
        print(json.dumps({key: value for key, value in report.items() if key != 'completed_frames'}, indent=2))


if __name__ == '__main__':
    main()
