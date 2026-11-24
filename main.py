#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261124.

Python 3.13, standard library only. Copies the pre-rendered entry.png
shipped in this repository to the output directory, after validating
it: PNG magic bytes, IHDR dimensions 1024x1024, size at most 1 MiB,
and every chunk's CRC32. No network, no environment secrets.

Usage: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
WANT_W, WANT_H = 1024, 1024


def fail(msg):
    raise SystemExit("entry.png validation failed: " + msg)


def validate(path):
    with open(path, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        fail("size %d exceeds %d bytes" % (len(data), MAX_BYTES))
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail("not a PNG file")
    off = 8
    width = height = None
    seen_iend = False
    while off + 12 <= len(data):
        (length,) = struct.unpack(">I", data[off:off + 4])
        ctype = data[off + 4:off + 8]
        end = off + 12 + length
        if end > len(data):
            fail("truncated chunk " + ctype.decode("latin-1"))
        chunk = data[off + 8:off + 8 + length]
        (crc_stored,) = struct.unpack(">I", data[off + 8 + length:end])
        if zlib.crc32(ctype + chunk) & 0xFFFFFFFF != crc_stored:
            fail("bad CRC in chunk " + ctype.decode("latin-1"))
        if ctype == b"IHDR":
            if length != 13:
                fail("bad IHDR length")
            width, height = struct.unpack(">II", chunk[:8])
        if ctype == b"IEND":
            seen_iend = True
            break
        off = end
    if not seen_iend:
        fail("missing IEND chunk")
    if (width, height) != (WANT_W, WANT_H):
        fail("dimensions %sx%s, expected 1024x1024" % (width, height))
    return data


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = validate(SRC)
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
