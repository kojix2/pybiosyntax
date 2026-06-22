#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Minimal Python ctypes example for libbiosyntax.

Usage with an explicit shared library path:
    python3 examples/ffi_ctypes_lowlevel.py /path/to/libbiosyntax.so
"""

from __future__ import annotations

import ctypes
import pathlib
import sys


class BiosynSpan(ctypes.Structure):
    _fields_ = [
        ("start", ctypes.c_uint64),
        ("length", ctypes.c_uint64),
        ("class_id", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]


def symbol(lib: ctypes.CDLL, *names: str):
    for name in names:
        try:
            return getattr(lib, name)
        except AttributeError:
            pass
    raise AttributeError(f"missing symbol: {' or '.join(names)}")


def main() -> int:
    root = pathlib.Path(__file__).resolve().parents[1]
    default_lib = root / "build" / "libbiosyntax.so"
    lib_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else default_lib
    lib = ctypes.CDLL(str(lib_path))

    lib.biosyn_format_from_name.argtypes = [ctypes.c_char_p]
    lib.biosyn_format_from_name.restype = ctypes.c_uint32

    highlight_line = symbol(lib, "biosyn_highlight_line", "biosyn_highlight_line_u64")
    highlight_line.argtypes = [
        ctypes.c_uint32,
        ctypes.c_char_p,
        ctypes.c_uint64,
        ctypes.c_uint64,
        ctypes.POINTER(BiosynSpan),
        ctypes.c_uint64,
    ]
    highlight_line.restype = ctypes.c_uint64

    lib.biosyn_class_name.argtypes = [ctypes.c_uint32]
    lib.biosyn_class_name.restype = ctypes.c_char_p

    line = b"chr1\t42\trs1\tA\tT\t99\tPASS\tDP=10;AF=0.5\n"
    fmt = lib.biosyn_format_from_name(b"vcf")
    spans = (BiosynSpan * 64)()
    n = highlight_line(fmt, line, len(line), 0, spans, len(spans))

    for i in range(min(n, len(spans))):
        cls = lib.biosyn_class_name(spans[i].class_id).decode("ascii")
        token = line[spans[i].start : spans[i].start + spans[i].length].decode("utf-8")
        print(f"{spans[i].start:02d}-{spans[i].start + spans[i].length:02d}\t{cls}\t{token!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
