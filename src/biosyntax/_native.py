# SPDX-License-Identifier: GPL-3.0-only
"""ctypes loader for the libbiosyntax C ABI."""

from __future__ import annotations

import ctypes
import ctypes.util
import os
import pathlib
import sys
from typing import Dict, Iterable, Optional, Sequence


class CSpan(ctypes.Structure):
    """ctypes representation of biosyn_span_t."""

    _fields_ = [
        ("start", ctypes.c_uint64),
        ("length", ctypes.c_uint64),
        ("class_id", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]


class CClassInfo(ctypes.Structure):
    """ctypes representation of biosyn_class_info_t."""

    _fields_ = [
        ("name", ctypes.c_char_p),
        ("scope", ctypes.c_char_p),
        ("foreground", ctypes.c_char_p),
        ("background", ctypes.c_char_p),
        ("font_style", ctypes.c_char_p),
        ("ansi_sgr", ctypes.c_char_p),
    ]


class CFormatInfo(ctypes.Structure):
    """ctypes representation of biosyn_format_info_t."""

    _fields_ = [
        ("name", ctypes.c_char_p),
        ("description", ctypes.c_char_p),
        ("stateful", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]


class CAnsiStyle(ctypes.Structure):
    """ctypes representation of biosyn_ansi_style_t."""

    _fields_ = [
        ("class_id", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
        ("ansi_sgr", ctypes.c_char_p),
    ]


def _platform_library_names() -> Iterable[str]:
    if sys.platform == "darwin":
        return ("libbiosyntax.dylib", "biosyntax.dylib", "libbiosyntax.so")
    if os.name == "nt":
        return ("biosyntax.dll", "libbiosyntax.dll")
    return ("libbiosyntax.so", "libbiosyntax.dylib")


def _candidate_paths(explicit_path: Optional[str]) -> Iterable[str]:
    if explicit_path:
        yield explicit_path

    env_path = os.environ.get("BIOSYNTAX_LIBRARY")
    if env_path:
        yield env_path

    package_dir = pathlib.Path(__file__).resolve().parent
    for name in _platform_library_names():
        yield str(package_dir / name)

    current = pathlib.Path(__file__).resolve()

    # Standalone package layout: src/biosyntax/_native.py -> project root.
    for name in _platform_library_names():
        yield str(current.parents[2] / "build" / name)

    # Upstream monorepo layout: bindings/python/src/biosyntax/_native.py -> project root.
    if len(current.parents) > 4:
        for name in _platform_library_names():
            yield str(current.parents[4] / "build" / name)

    found = ctypes.util.find_library("biosyntax")
    if found:
        yield found

    for name in _platform_library_names():
        yield name


class Native:
    """Loaded libbiosyntax shared library with configured ctypes signatures."""

    def __init__(self, library_path: Optional[str] = None) -> None:
        errors = []
        self.path = None  # type: Optional[str]
        self.lib = None
        seen = set()
        for candidate in _candidate_paths(library_path):
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            try:
                self.lib = ctypes.CDLL(candidate)
                self.path = candidate
                break
            except OSError as exc:
                errors.append(f"{candidate}: {exc}")
        if self.lib is None:
            detail = "\n".join(errors[-8:])
            raise RuntimeError(
                "Could not load libbiosyntax. Build the C shared library first "
                "and set BIOSYNTAX_LIBRARY=/path/to/libbiosyntax.so."
                + ("\nRecent load attempts:\n" + detail if detail else "")
            )
        self._configure()

    @staticmethod
    def _configure_function(
        lib: ctypes.CDLL,
        names: Sequence[str],
        argtypes: Sequence[object],
        restype: object,
        alias: Optional[str] = None,
    ) -> object:
        """Configure the first available symbol and optionally expose an alias."""

        last_error = None
        for name in names:
            try:
                function = getattr(lib, name)
                function.argtypes = list(argtypes)
                function.restype = restype
                if alias:
                    setattr(lib, alias, function)
                return function
            except AttributeError as exc:
                last_error = exc
        joined = " or ".join(names)
        raise AttributeError(f"libbiosyntax does not export {joined}") from last_error

    def _configure(self) -> None:
        assert self.lib is not None
        lib = self.lib

        lib.biosyn_abi_version.argtypes = []
        lib.biosyn_abi_version.restype = ctypes.c_uint32

        lib.biosyn_version.argtypes = []
        lib.biosyn_version.restype = ctypes.c_char_p

        lib.biosyn_format_from_name.argtypes = [ctypes.c_char_p]
        lib.biosyn_format_from_name.restype = ctypes.c_uint32

        lib.biosyn_guess_format_from_path.argtypes = [ctypes.c_char_p]
        lib.biosyn_guess_format_from_path.restype = ctypes.c_uint32

        lib.biosyn_format_name.argtypes = [ctypes.c_uint32]
        lib.biosyn_format_name.restype = ctypes.c_char_p

        lib.biosyn_format_count.argtypes = []
        lib.biosyn_format_count.restype = ctypes.c_uint32

        lib.biosyn_format_info.argtypes = [ctypes.c_uint32, ctypes.POINTER(CFormatInfo)]
        lib.biosyn_format_info.restype = ctypes.c_int

        lib.biosyn_class_name.argtypes = [ctypes.c_uint32]
        lib.biosyn_class_name.restype = ctypes.c_char_p

        lib.biosyn_class_scope.argtypes = [ctypes.c_uint32]
        lib.biosyn_class_scope.restype = ctypes.c_char_p

        lib.biosyn_class_ansi_sgr.argtypes = [ctypes.c_uint32]
        lib.biosyn_class_ansi_sgr.restype = ctypes.c_char_p

        lib.biosyn_class_default_foreground.argtypes = [ctypes.c_uint32]
        lib.biosyn_class_default_foreground.restype = ctypes.c_char_p

        lib.biosyn_class_default_background.argtypes = [ctypes.c_uint32]
        lib.biosyn_class_default_background.restype = ctypes.c_char_p

        lib.biosyn_class_default_font_style.argtypes = [ctypes.c_uint32]
        lib.biosyn_class_default_font_style.restype = ctypes.c_char_p

        lib.biosyn_class_count.argtypes = []
        lib.biosyn_class_count.restype = ctypes.c_uint32

        lib.biosyn_class_info.argtypes = [ctypes.c_uint32, ctypes.POINTER(CClassInfo)]
        lib.biosyn_class_info.restype = ctypes.c_int

        lib.biosyn_state_new.argtypes = [ctypes.c_uint32]
        lib.biosyn_state_new.restype = ctypes.c_void_p

        lib.biosyn_state_free.argtypes = [ctypes.c_void_p]
        lib.biosyn_state_free.restype = None

        self._configure_function(
            lib,
            ("biosyn_highlight_line", "biosyn_highlight_line_u64"),
            [
                ctypes.c_uint32,
                ctypes.c_char_p,
                ctypes.c_uint64,
                ctypes.c_uint64,
                ctypes.POINTER(CSpan),
                ctypes.c_uint64,
            ],
            ctypes.c_uint64,
            alias="biosyn_highlight_line_u64",
        )

        self._configure_function(
            lib,
            ("biosyn_highlight_next_line", "biosyn_highlight_next_line_u64"),
            [
                ctypes.c_void_p,
                ctypes.c_char_p,
                ctypes.c_uint64,
                ctypes.POINTER(CSpan),
                ctypes.c_uint64,
            ],
            ctypes.c_uint64,
            alias="biosyn_highlight_next_line_u64",
        )

        self._configure_function(
            lib,
            ("biosyn_render_ansi_line", "biosyn_render_ansi_line_u64"),
            [
                ctypes.c_char_p,
                ctypes.c_uint64,
                ctypes.POINTER(CSpan),
                ctypes.c_uint64,
                ctypes.c_char_p,
                ctypes.c_uint64,
            ],
            ctypes.c_uint64,
            alias="biosyn_render_ansi_line_u64",
        )

        self._configure_function(
            lib,
            ("biosyn_render_ansi_line_with_styles", "biosyn_render_ansi_line_with_styles_u64"),
            [
                ctypes.c_char_p,
                ctypes.c_uint64,
                ctypes.POINTER(CSpan),
                ctypes.c_uint64,
                ctypes.POINTER(CAnsiStyle),
                ctypes.c_uint64,
                ctypes.c_char_p,
                ctypes.c_uint64,
            ],
            ctypes.c_uint64,
            alias="biosyn_render_ansi_line_with_styles_u64",
        )


_CACHE = {}  # type: Dict[Optional[str], Native]


def load_native(library_path: Optional[str] = None) -> Native:
    key = str(library_path) if library_path is not None else None
    native = _CACHE.get(key)
    if native is None:
        native = Native(key)
        _CACHE[key] = native
    return native
