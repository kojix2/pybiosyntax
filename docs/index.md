# pybiosyntax

pybiosyntax provides Python bindings for libbiosyntax.

The package vendors the libbiosyntax C core.
Source installs build the bundled C library.
Wheels include the compiled shared library.

## Install

```sh
python -m pip install .
```

No separate libbiosyntax installation is required.

## Basic usage

```python
import biosyntax as bs

line = "chr1\t42\trs1\tA\tT\t99\tPASS\n"
for span in bs.highlight_line("vcf", line):
    print(span, bs.class_name(span.class_id), span.slice(line))
```

## Command line

```sh
biosyntax sample.vcf
python -m biosyntax --format fastq reads.fastq
```

## Documentation

- [Installation](installation.md)
- [Usage](usage.md)
- [API reference](api.md)
- [Command line](cli.md)
- [Development](development.md)
- [Vendoring](vendoring.md)
