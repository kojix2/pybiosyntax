# SPDX-License-Identifier: GPL-3.0-only
from __future__ import annotations

import io
import os
import tempfile
import unittest

import biosyntax as bs
from biosyntax.__main__ import main as cli_main


class PythonBindingTests(unittest.TestCase):
    def test_version_and_format_helpers(self) -> None:
        self.assertEqual(bs.abi_version(), 1)
        self.assertRegex(bs.version(), r"^\d+\.\d+\.\d+$")
        self.assertEqual(bs.format_from_name("vcf"), bs.Format.VCF)
        self.assertEqual(bs.guess_format_from_path("sample.fastq.gz"), bs.Format.FASTQ)
        self.assertEqual(bs.format_name(bs.Format.GTF), "gtf")
        self.assertEqual(bs.format_from_name("fasta-orf"), bs.Format.FASTA_ORF)
        self.assertEqual(bs.format_name(bs.Format.FASTA_ORF), "fasta-orf")

    def test_vcf_highlight(self) -> None:
        line = "chr1\t42\trs1\tA\tT\t99\tPASS\tDP=10;AF=0.5\tGT:DP\t0/1:10\n"
        spans = bs.highlight_line("vcf", line)
        names = [bs.class_name(span.class_id) for span in spans]
        self.assertIn("chrom", names)
        self.assertIn("position", names)
        self.assertIn("good", names)
        self.assertIn("keyword6", names)
        self.assertIn("number", names)
        self.assertIn("null", names)
        self.assertTrue(any(span.slice(line) == "PASS" for span in spans))

    def test_fasta_bytes(self) -> None:
        line = b"ACGTN-\n"
        spans = bs.highlight_line(bs.Format.FASTA, line, line_no=1)
        names = [bs.class_name(span.class_id) for span in spans]
        self.assertIn("nt_a", names)
        self.assertIn("nt_c", names)
        self.assertIn("nt_g", names)
        self.assertIn("nt_t", names)
        self.assertIn("nt_n", names)
        self.assertIn("gap", names)
        self.assertIsInstance(spans[0].slice(line), bytes)


    def test_fasta_schemes_and_theme_helpers(self) -> None:
        self.assertEqual(bs.format_from_name("fasta-zappo"), bs.Format.FASTA_ZAPPO)
        spans = bs.highlight_line(bs.Format.FASTA_NT, "ARYN-\n")
        names = [bs.class_name(span.class_id) for span in spans]
        self.assertIn("nt_r", names)
        self.assertIn("nt_y", names)
        self.assertIn("gap", names)

        spans = bs.highlight_line("fasta-zappo", "ARZ\n")
        names = [bs.class_name(span.class_id) for span in spans]
        self.assertIn("zappo_a", names)
        self.assertIn("zappo_r", names)
        self.assertIn("zappo_z", names)
        nt_a = bs.highlight_line("fasta-nt", "A\n")[0].class_id
        self.assertTrue(bs.class_default_foreground(nt_a).startswith("#"))
        self.assertNotEqual(bs.class_ansi_sgr(nt_a), "")
        info = bs.class_info(nt_a)
        self.assertEqual(info.name, "nt_a")
        self.assertEqual(info.foreground, bs.class_default_foreground(nt_a))
        self.assertGreater(bs.class_count(), nt_a)
        self.assertEqual(bs.classes()["nt_a"], nt_a)
        self.assertEqual(bs.class_infos()["nt_a"].scope, info.scope)
        self.assertEqual(bs.formats()["vcf"], bs.Format.VCF)
        self.assertGreater(bs.format_count(), bs.Format.FASTA_ORF)
        self.assertFalse(bs.format_info("vcf").stateful)
        self.assertTrue(bs.format_info(bs.Format.FASTQ).stateful)
        self.assertEqual(bs.format_infos()["fasta-orf"].description, bs.format_info("fasta-orf").description)

        spans = bs.highlight_line(bs.Format.FASTA_ORF, "CCCATGAAATAGCCC\n")
        names = [bs.class_name(span.class_id) for span in spans]
        self.assertIn("orf_start", names)
        self.assertIn("orf_coding", names)
        self.assertIn("orf_stop", names)

    def test_fastq_state(self) -> None:
        with bs.State(bs.Format.FASTQ) as state:
            lines = ["@r1\n", "ACGT\n", "+\n", "IIII\n"]
            classes = [[bs.class_name(span.class_id) for span in state.highlight_line(line)] for line in lines]
        self.assertIn("header", classes[0])
        self.assertIn("nt_a", classes[1])
        self.assertIn("header", classes[2])
        self.assertIn("qual_10i", classes[3])

        streamed = list(bs.highlight_lines(bs.Format.FASTQ, lines))
        streamed_classes = [[bs.class_name(span.class_id) for span in spans] for spans in streamed]
        self.assertIn("qual_10i", streamed_classes[3])

    def test_render_ansi_line(self) -> None:
        rendered = bs.render_ansi_line("vcf", "chr1\t42\trs1\tA\tT\t99\tPASS\n")
        self.assertIn("\x1b[", rendered)
        self.assertIn("PASS", rendered)
        custom = bs.render_ansi_line("vcf", "chr1\t42\trs1\tA\tT\t99\tPASS\n", theme={"good": "1;31"})
        self.assertIn("\x1b[1;31mPASS", custom)

        rendered_lines = list(bs.render_ansi_lines("vcf", ["chr1\t42\trs1\tA\tT\t99\tPASS\n"]))
        self.assertEqual(len(rendered_lines), 1)
        self.assertIn("PASS", rendered_lines[0])

    def test_cli(self) -> None:
        out = io.StringIO()
        with tempfile.NamedTemporaryFile("w", suffix=".vcf", delete=False) as handle:
            handle.write("chr1\t42\trs1\tA\tT\t99\tPASS\n")
            path = handle.name
        try:
            rc = cli_main([path], stdout=out)
            self.assertEqual(rc, 0)
            self.assertIn("PASS", out.getvalue())
            self.assertIn("\x1b[", out.getvalue())
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
