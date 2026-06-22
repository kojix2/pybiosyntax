# Installation

pybiosyntax requires Python 3.10 or later.

## Install from the source tree

From the project root:

```sh
python -m pip install .
```

When installed from source, pybiosyntax builds the bundled `libbiosyntax` C
library. When installed from a wheel, the compiled shared library is already
included in the wheel.

The installed Python package contains the shared library.
Users do not need to install `libbiosyntax` separately.

## Development install

For local development, reinstall after changes.
This includes Python code, packaging files, and vendored C source.

```sh
python -m pip install .
python examples/basic.py
```

Editable installs are not recommended for this project.
The package includes a bundled shared library.
The normal build step produces that library.

## Build distributions

To build a source distribution and wheel:

```sh
python -m pip install build
python -m build
```

Wheels are platform-specific.
They contain a compiled shared library.
