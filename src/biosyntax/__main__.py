# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations

import argparse
import sys
from typing import Iterable, Optional, TextIO

from . import Format, format_from_name, guess_format_from_path, render_ansi_lines


def _input_lines(path: Optional[str]) -> Iterable[str]:
    if not path or path == "-":
        yield from sys.stdin
        return
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        yield from handle


def _resolve_format(name: Optional[str], path: Optional[str]) -> Format:
    if name:
        return format_from_name(name)
    if path and path != "-":
        guessed = guess_format_from_path(path)
        if guessed != Format.UNKNOWN:
            return guessed
    return Format.UNKNOWN


def main(argv: Optional[Iterable[str]] = None, stdout: Optional[TextIO] = None) -> int:
    parser = argparse.ArgumentParser(description="Render biological text files with libbiosyntax ANSI highlighting.")
    parser.add_argument("path", nargs="?", help="input file, or stdin when omitted")
    parser.add_argument("-f", "--format", help="format name such as fasta, fastq, sam, vcf, bed, gtf, gff, pdb, or wig")
    parser.add_argument("--library", help="override libbiosyntax shared library path")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout if stdout is not None else sys.stdout
    fmt = _resolve_format(args.format, args.path)
    for rendered in render_ansi_lines(fmt, _input_lines(args.path), library_path=args.library):
        out.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
