# pybiosyntax

[![CI](https://github.com/kojix2/pybiosyntax/actions/workflows/ci.yml/badge.svg)](https://github.com/kojix2/pybiosyntax/actions/workflows/ci.yml)


[pybiosyntax](https://github.com/kojix2/pybiosyntax) provides Python bindings for [libbiosyntax](https://github.com/kojix2/libbiosyntax).

The C core is vendored under `vendor/libbiosyntax` and is built automatically
when installing the Python package:

```sh
python -m pip install .
```

The bundled C library is installed inside the Python package, so no separate
libbiosyntax installation is required.

## Usage

```python
import biosyntax as bs

line = "chr1\t42\trs1\tA\tT\t99\tPASS\n"
for span in bs.highlight_line("vcf", line):
    print(span, bs.class_name(span.class_id), span.slice(line))
```

The package also installs a small ANSI-rendering CLI:

```sh
biosyntax sample.vcf
python -m biosyntax --format fastq reads.fastq
```

For source-tree development, reinstall after changes so the bundled shared
library is rebuilt and installed with the package:

```sh
python -m pip install .
python examples/basic.py
```

To build distribution artifacts, use a PEP 517 frontend such as `build`:

```sh
python -m pip install build
python -m build
```
