"""Safety/failure checks plus real OIDN inference when its pinned runtime is installed."""
import hashlib
import io
import json
import os
from pathlib import Path
import random
import shutil
import struct
import tarfile
import tempfile
import unittest
from unittest import mock
import zlib

from denoise import (denoise_frames, denoise_image, executable_path,
                     png_dimensions, verify_archive, _safe_extract)


def write_png(path, width=32, height=32):
    rng = random.Random(234)
    rows = []
    for y in range(height):
        pixels = bytearray()
        for x in range(width):
            base = 65 if x < width//2 else 190
            pixels.extend(max(0, min(255, base+rng.randint(-22,22))) for _ in range(3))
        rows.append(b'\0'+pixels)
    def chunk(kind, data):
        return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data)&0xffffffff)
    Path(path).write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB',width,height,8,2,0,0,0))+
                           chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b''))


class DenoiseTests(unittest.TestCase):
    def test_wrong_archive_digest_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'untrusted.tar.gz'
            path.write_bytes(b'not the official pinned archive')
            with self.assertRaisesRegex(ValueError,'SHA-256 mismatch'):
                verify_archive(path)

    def test_archive_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'escape.tar.gz'
            with tarfile.open(path,'w:gz') as archive:
                entry=tarfile.TarInfo('../escape')
                entry.size=1
                archive.addfile(entry,io.BytesIO(b'x'))
            with self.assertRaisesRegex(ValueError,'Unsafe'):
                _safe_extract(path,Path(directory)/'install')
            self.assertFalse((Path(directory)/'escape').exists())

    def test_raw_image_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'raw.png'
            write_png(path)
            before=path.read_bytes()
            with self.assertRaisesRegex(ValueError,'preserved raw input'):
                denoise_image(path,path)
            self.assertEqual(path.read_bytes(),before)

    def test_empty_sequence_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,'No frames'):
                denoise_frames(Path(directory)/'raw',Path(directory)/'clean')

    def test_stale_derivative_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            raw=Path(directory)/'raw';raw.mkdir()
            clean=Path(directory)/'clean';clean.mkdir()
            write_png(raw/'frame_0001.png')
            write_png(clean/'frame_9999.png')
            with self.assertRaisesRegex(ValueError,'Stale'):
                denoise_frames(raw,clean)

    def test_failure_report_never_claims_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            raw=Path(directory)/'raw';raw.mkdir()
            clean=Path(directory)/'clean'
            for i in (1,2):write_png(raw/f'frame_{i:04d}.png')
            def simulated(source,destination,*args):
                if source.name=='frame_0002.png':raise RuntimeError('inference interrupted')
                shutil.copyfile(source,destination)
                return {'source_sha256':'source','output_sha256':'output','seconds':1}
            with mock.patch('denoise.denoise_image',side_effect=simulated):
                with self.assertRaisesRegex(RuntimeError,'interrupted'):
                    denoise_frames(raw,clean,Path('/unused/pinned/runtime'))
            report=json.loads((clean/'denoise_report.json').read_text())
            self.assertEqual(report['status'],'failed')
            self.assertEqual(len(report['completed_frames']),1)
            self.assertEqual(report['source_frames'],2)

    def test_bad_png_header_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'bad.png';path.write_bytes(b'not a png')
            with self.assertRaises(ValueError):png_dimensions(path)

    def test_real_oidn_preserves_raw_and_dimensions(self):
        try:program=executable_path()
        except RuntimeError:self.skipTest('Install pinned OIDN / set GARAGE_OIDN_ROOT for real inference test')
        if not shutil.which('ffmpeg'):self.skipTest('FFmpeg is not installed')
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'raw.png';destination=Path(directory)/'clean.png'
            write_png(source)
            before=hashlib.sha256(source.read_bytes()).hexdigest()
            report=denoise_image(source,destination,program)
            self.assertEqual(png_dimensions(destination),(32,32))
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),before)
            self.assertEqual(report['source_sha256'],before)
            self.assertNotEqual(report['source_sha256'],report['output_sha256'])
            self.assertEqual(report['status'],'denoised_and_verified')
            self.assertFalse(report['temporal_filtering'])


if __name__=='__main__':unittest.main()
