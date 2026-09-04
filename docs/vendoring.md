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
4. Replace `vendor/libbiosyntax/LICENSE.md` if the upstream license changed.
5. Update the Python package version in `pyproject.toml` as appropriate.
6. Run the Python tests.
7. Build the source distribution and wheel.

The bundled C library version is reported at runtime by
`biosyntax.version()` and is defined by the version macros in the vendored
header. Tests validate its version format without duplicating a release number.

Example commands:

```sh
python -m pip install .
python -m unittest discover -s tests
python -m pip install build
python -m build
```

## License

The Python binding is licensed under the MIT License.
See [`LICENSE.md`](https://github.com/kojix2/pybiosyntax/blob/main/LICENSE.md).

The vendored C code is licensed under the GNU Lesser General Public License
version 2.1 or later (`LGPL-2.1-or-later`).
See [`vendor/libbiosyntax/LICENSE.md`](https://github.com/kojix2/pybiosyntax/blob/main/vendor/libbiosyntax/LICENSE.md).
