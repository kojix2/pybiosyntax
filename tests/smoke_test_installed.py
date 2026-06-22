# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations

import biosyntax as bs


def main() -> None:
    line = "chr1\t42\trs1\tA\tT\t99\tPASS\n"
    spans = bs.highlight_line("vcf", line)
    names = {bs.class_name(span.class_id) for span in spans}

    assert bs.abi_version() >= 1
    assert bs.version()
    assert "chrom" in names
    assert "position" in names
    assert "good" in names
    assert "PASS" in bs.render_ansi_line("vcf", line)


if __name__ == "__main__":
    main()
