# Development

## Requirements

- Python 3.10 or later
- A C compiler
- `pip`

A C compiler is required for source installs.
The package builds the bundled `libbiosyntax` shared library during
installation.

## Install locally

From the project root:

```sh
python -m pip install .
```

Re-run the install command after changes.
This includes package code, build configuration, and vendored C code.

## Run tests

```sh
python -m unittest discover -s tests
```

## Run examples

```sh
python examples/basic.py
```

## Build distributions

```sh
python -m pip install build
python -m build
```

The output is written to `dist/`.
This local wheel is only for local testing.
Release wheels are built with `cibuildwheel`.

## Continuous integration

GitHub Actions runs the test suite on Linux, macOS, and Windows.
It uses the supported Python versions.
It also builds the source distribution and a local wheel.
The workflow checks that the bundled C source is present in the source distribution.
It checks that the bundled shared library is present in the wheel.

## Release wheels

The publish workflow uses `cibuildwheel`.
It builds manylinux, macOS, and Windows wheels.
Each wheel is tested after it is built.
The source distribution is built in a separate job.
The publish job uploads all artifacts to PyPI.
musllinux wheels are not built.
Windows ARM64 wheels are not built.

## Notes

Editable installs are not recommended for this project.
The installed package needs the compiled bundled shared library.
The normal build path produces that library.
