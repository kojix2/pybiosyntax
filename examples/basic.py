#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Small demo for the high-level Python binding.

Run after installing the package:

    python examples/basic.py
"""

from __future__ import annotations

import biosyntax as bs


def main() -> int:
    line = "chr1\t42\trs1\tA\tT\t99\tPASS\tDP=10;AF=0.5\n"
    for span in bs.highlight_line(bs.Format.VCF, line):
        print(f"{span.start:02d}-{span.end:02d}\t{bs.class_name(span.class_id)}\t{span.slice(line)!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
