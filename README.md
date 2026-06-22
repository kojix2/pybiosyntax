# pybiosyntax

`pybiosyntax` provides Python bindings for `libbiosyntax`.

The C core is vendored under `vendor/libbiosyntax` and is built automatically
when installing the Python package:

```sh
python -m pip install .
```

After installation, no `BIOSYNTAX_LIBRARY` setting is needed. The shared library
is loaded from the installed `biosyntax` package directory.

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

For source-tree development, use an editable install so the bundled shared
library is built through the normal packaging path:

```sh
python -m pip install -e .
python examples/basic.py
```

To build distribution artifacts, use a PEP 517 frontend such as `build`:

```sh
python -m pip install build
python -m build
```

Set `BIOSYNTAX_LIBRARY=/path/to/libbiosyntax.so` to override the bundled
library at runtime. Set `BIOSYNTAX_SKIP_BUNDLED_BUILD=1` only when you
intentionally want to build a package without the bundled shared library.
