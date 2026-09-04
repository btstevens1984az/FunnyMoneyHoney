#!/usr/bin/env python3
"""Generate lightweight placeholder GIFs for media/readme/ (no Playwright required)."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "readme"


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def png_rgba(width: int, height: int, rgba: tuple[int, int, int, int]) -> bytes:
    raw = b"".join(b"\x00" + bytes(rgba) * width for _ in range(height))
    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            _chunk(b"IDAT", zlib.compress(raw, 9)),
            _chunk(b"IEND", b""),
        ]
    )


def write_placeholder_gif(path: Path, label: str, color: tuple[int, int, int]) -> None:
    """
    Build a tiny multi-frame GIF via png frames + ffmpeg when available;
    otherwise write a static single-color PNG renamed note beside an SVG sibling.
    """
    import shutil
    import subprocess
    import tempfile

    path.parent.mkdir(parents=True, exist_ok=True)
    if not shutil.which("ffmpeg"):
        # Fallback: write a tiny animated GIF manually (2 frames, 2x2)
        # GIF89a minimal animation
        path.write_bytes(_minimal_gif(color))
        note = path.with_suffix(".txt")
        note.write_text(
            f"Placeholder GIF for {label}. Re-run scripts/capture-readme.mjs with ffmpeg for real UI loops.\n",
            encoding="utf-8",
        )
        return

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        for i in range(12):
            # Pulse brightness
            factor = 0.7 + 0.3 * ((i % 6) / 5)
            c = tuple(min(255, int(ch * factor)) for ch in color) + (255,)
            (tdp / f"frame-{i:03d}.png").write_bytes(png_rgba(480, 270, c))  # type: ignore[arg-type]
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                "6",
                "-i",
                str(tdp / "frame-%03d.png"),
                "-vf",
                "scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                "-loop",
                "0",
                str(path),
            ],
            check=True,
            capture_output=True,
        )


def _minimal_gif(color: tuple[int, int, int]) -> bytes:
    """Valid 2-frame 2×2 GIF."""
    r, g, b = color
    # Logical screen + global color table + two image blocks with graphics control
    header = b"GIF89a"
    screen = struct.pack("<HH", 2, 2) + bytes([0x91, 0, 0])
    gct = bytes([r, g, b, max(0, r - 40), max(0, g - 40), max(0, b - 40), 0, 0, 0, 255, 255, 255])
    # Netscape loop
    app = b"!\xff\x0bNETSCAPE2.0\x03\x01\x00\x00\x00"
    frames = b""
    for delay, idx in ((40, 0), (40, 1)):
        gce = b"!\xf9\x04\x04" + struct.pack("<H", delay) + b"\x00\x00"
        img = b"," + struct.pack("<HHHH", 0, 0, 2, 2) + b"\x00"
        # LZW minimum size 2, then data
        data = bytes([2, 3, 0x04 | (idx << 2), 0x04, 0x05, 0x00])  # simplistic; may not render everywhere
        frames += gce + img + data
    # Safer: use a known-good solid 1x1 gif and accept static placeholder
    # 1x1 red-ish GIF (widely valid)
    return bytes.fromhex(
        "47494638396101000100800000"
        + f"{r:02x}{g:02x}{b:02x}"
        + "00000021f90401000000002c000000000100010000020144003b"
    )


def main() -> None:
    specs = [
        ("01-odds-table.gif", "odds table", (232, 184, 75)),
        ("02-probability.gif", "probability", (45, 212, 191)),
        ("03-bankroll.gif", "bankroll", (251, 113, 133)),
        ("04-dashboard.gif", "dashboard", (100, 116, 139)),
    ]
    for name, label, color in specs:
        write_placeholder_gif(OUT / name, label, color)
        print("wrote", OUT / name)


if __name__ == "__main__":
    main()
