# Vendoring

pybiosyntax vendors the small C core from `libbiosyntax`.

Upstream repository:

```text
https://github.com/kojix2/libbiosyntax
```

Vendored files:

```text
vendor/libbiosyntax/include/biosyntax.h
vendor/libbiosyntax/src/biosyntax.c
```

For source installs, the vendored C code is built into a shared library.
The shared library is installed inside the `biosyntax` Python package.
Built wheels already contain this shared library.

## Why vendor the C source?

Vendoring keeps installation self-contained.
Users do not need a separate `libbiosyntax` installation.
Wheels contain the native library loaded at runtime.

This layout fits this project.
The C core is small.
It has no runtime dependencies.
It is designed to be copied into other projects.

## Updating the vendored code

To update the vendored code:

1. Check the upstream `libbiosyntax` changes.
2. Replace `vendor/libbiosyntax/include/biosyntax.h`.
3. Replace `vendor/libbiosyntax/src/biosyntax.c`.
4. Run the Python tests.
5. Build the source distribution and wheel.

Example commands:

```sh
python -m pip install .
python -m unittest discover -s tests
python -m pip install build
python -m build
```

## License

The vendored C code is GPL-3.0-only. The Python package uses the same license.
See `LICENSE.md`.
