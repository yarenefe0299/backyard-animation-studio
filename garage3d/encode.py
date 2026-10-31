#!/usr/bin/env python3
"""Encode a complete Blender PNG sequence; never manufacture missing frames."""

import argparse
import json
import math
import os
from pathlib import Path
import struct
import subprocess
from fractions import Fraction


def inspect_sequence(directory, frames=120):
    directory = Path(directory)
    if frames < 2:
        raise ValueError("An animated preview needs at least two frames")
    expected = {f"frame_{number:04d}.png" for number in range(1, frames + 1)}
    actual = {path.name for path in directory.glob("frame_*.png")}
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(f"Incomplete or stale frame sequence: missing={missing[:8]}, extra={extra[:8]}")
    dimensions = None
    for filename in sorted(expected):
        with (directory / filename).open("rb") as source:
            header = source.read(24)
        if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
            raise ValueError(f"Invalid PNG header: {filename}")
        size = struct.unpack(">II", header[16:24])
        if not all(size) or any(value % 2 for value in size):
            raise ValueError(f"H.264 yuv420p needs positive even dimensions: {filename}: {size}")
        if dimensions is not None and size != dimensions:
            raise ValueError(f"Frame dimensions changed: {filename}: {size} != {dimensions}")
        dimensions = size
    return dimensions


def encode(output, frames=120, fps=30):
    output = Path(output).resolve()
    if fps < 1:
        raise ValueError("FPS must be positive")
    destination = output / "style-test.mp4"
    temporary = output / ".style-test.encoding.mp4"
    report_path = output / "video_report.json"
    # A failed rerun must not leave an old success report or video in its place.
    destination.unlink(missing_ok=True)
    report_path.unlink(missing_ok=True)
    width, height = inspect_sequence(output / "frames", frames)
    try:
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
            "-framerate", str(fps), "-start_number", "1",
            "-i", str(output / "frames" / "frame_%04d.png"),
            "-frames:v", str(frames), "-an", "-c:v", "libx264",
            "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
            "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709",
            "-vf", "scale=out_color_matrix=bt709:out_range=tv",
            "-colorspace", "bt709", "-color_primaries", "bt709",
            "-color_trc", "bt709", "-color_range", "tv",
            "-movflags", "+faststart", str(temporary),
        ], check=True)
        result = subprocess.run([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-count_frames", "-show_entries",
            "stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_read_frames,duration,color_space,color_transfer,color_primaries,color_range",
            "-of", "json", str(temporary),
        ], check=True, capture_output=True, text=True)
        streams = json.loads(result.stdout)["streams"]
        if len(streams) != 1:
            raise ValueError("Expected one video stream")
        video = streams[0]
        expected = {
            "codec_name": "h264", "pix_fmt": "yuv420p", "width": width,
            "height": height, "nb_read_frames": str(frames),
            "color_space": "bt709", "color_transfer": "bt709",
            "color_primaries": "bt709", "color_range": "tv",
        }
        for field, value in expected.items():
            if video.get(field) != value:
                raise ValueError(f"Encoded {field}: {video.get(field)!r}; expected {value!r}")
        if Fraction(video["r_frame_rate"]) != fps:
            raise ValueError(f"Encoded frame rate is not {fps}")
        if not math.isclose(float(video["duration"]), frames / fps, abs_tol=1 / fps):
            raise ValueError("Encoded duration does not match the frame sequence")
        os.replace(temporary, destination)
        report = {
            "status": "encoded_and_verified", "video": destination.name,
            "source_frames": frames, "fps": fps, "duration_seconds": frames / fps,
            "stream": video,
            "scope": "Animated 3D style test; visual approval remains pending",
        }
        report_path.write_text(json.dumps(report, indent=2) + "\n")
        return report
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("garage3d/output"))
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--fps", type=int, default=30)
    arguments = parser.parse_args()
    print(json.dumps(encode(arguments.output, arguments.frames, arguments.fps), indent=2))


if __name__ == "__main__":
    main()
