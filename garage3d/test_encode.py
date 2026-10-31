"""Sequence integrity tests plus a real FFmpeg/FFprobe integration check."""

import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from encode import encode, inspect_sequence


def png(path, width=16, height=28, color=(128, 160, 192)):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    pixels = (b"\x00" + bytes(color) * width) * height
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")
    )


class EncoderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.output = Path(self.temporary.name)
        self.frames = self.output / "frames"
        self.frames.mkdir()
        for number in range(1, 4):
            png(self.frames / f"frame_{number:04d}.png", color=(number * 60, 100, 140))

    def tearDown(self):
        self.temporary.cleanup()

    def test_complete_sequence_dimensions(self):
        self.assertEqual(inspect_sequence(self.frames, 3), (16, 28))

    def test_missing_frame_rejected_before_encoding(self):
        (self.frames / "frame_0002.png").unlink()
        with patch("encode.subprocess.run") as run:
            with self.assertRaisesRegex(ValueError, "Incomplete"):
                encode(self.output, 3)
            run.assert_not_called()

    def test_stale_extra_frame_rejected(self):
        png(self.frames / "frame_0004.png")
        with self.assertRaisesRegex(ValueError, "extra="):
            inspect_sequence(self.frames, 3)

    def test_dimensions_must_stay_consistent(self):
        png(self.frames / "frame_0002.png", width=18)
        with self.assertRaisesRegex(ValueError, "dimensions changed"):
            inspect_sequence(self.frames, 3)

    def test_failed_rerun_clears_stale_success(self):
        (self.output / "style-test.mp4").write_bytes(b"old video")
        (self.output / "video_report.json").write_text('{"status":"old"}')
        (self.frames / "frame_0002.png").unlink()
        with self.assertRaises(ValueError):
            encode(self.output, 3)
        self.assertFalse((self.output / "style-test.mp4").exists())
        self.assertFalse((self.output / "video_report.json").exists())

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "Needs FFmpeg and FFprobe")
    def test_real_h264_round_trip(self):
        result = encode(self.output, 3, 30)
        self.assertEqual(result["status"], "encoded_and_verified")
        self.assertEqual(result["stream"]["nb_read_frames"], "3")
        self.assertEqual(result["stream"]["color_space"], "bt709")
        self.assertTrue((self.output / "style-test.mp4").stat().st_size > 0)
        self.assertEqual(json.loads((self.output / "video_report.json").read_text()), result)


if __name__ == "__main__":
    unittest.main()
