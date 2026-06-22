# SPDX-License-Identifier: GPL-3.0-only
"""Python bindings for libbiosyntax.

The binding uses the libbiosyntax C shared library through ``ctypes`` and adds no
runtime dependencies. Span offsets and lengths are byte-based because they come
directly from the C tokenizer. When a Python ``str`` is passed, it is encoded as
UTF-8 before tokenization.
"""

from __future__ import annotations

import ctypes
import threading
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple, Union

from ._native import CAnsiStyle, CClassInfo, CFormatInfo, CSpan, Native, load_native

BytesLike = Union[str, bytes, bytearray, memoryview]
FormatLike = Union[int, str, "Format"]
ClassLike = int
ThemeLike = Mapping[Union[int, str], str]


class Format(IntEnum):
    UNKNOWN = 0
    FASTA = 1
    FASTQ = 2
    SAM = 3
    VCF = 4
    BED = 5
    GTF = 6
    GFF = 7
    PDB = 8
    CLUSTAL = 9
    FAIDX = 10
    FLAGSTAT = 11
    WIG = 12
    FASTA_NT = 13
    FASTA_HC = 14
    FASTA_CLUSTAL = 15
    FASTA_HYDRO = 16
    FASTA_TAYLOR = 17
    FASTA_ZAPPO = 18
    FASTA_ORF = 19


@dataclass(frozen=True)
class Span:
    """A highlighted byte range returned by libbiosyntax."""

    start: int
    length: int
    class_id: int

    @property
    def end(self) -> int:
        return self.start + self.length

    def slice(self, data: BytesLike, encoding: str = "utf-8", errors: str = "replace") -> Union[str, bytes]:
        """Return the token covered by this span.

        The return type follows the input type: ``str`` input returns ``str``;
        bytes-like input returns ``bytes``.
        """

        raw = _as_bytes(data)[self.start : self.end]
        if isinstance(data, str):
            return raw.decode(encoding, errors=errors)
        return raw


@dataclass(frozen=True)
class ClassInfo:
    """Built-in metadata for one token class."""

    name: str
    scope: str
    foreground: str
    background: str
    font_style: str
    ansi_sgr: str


@dataclass(frozen=True)
class FormatInfo:
    """Built-in metadata for one supported format."""

    name: str
    description: str
    stateful: bool


def _decode(c_string: bytes) -> str:
    return c_string.decode("ascii")


def _as_bytes(data: BytesLike) -> bytes:
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return bytes(data)
    if isinstance(data, memoryview):
        return data.tobytes()
    if isinstance(data, str):
        return data.encode("utf-8")
    raise TypeError("expected str, bytes, bytearray, or memoryview")


def _coerce_format(value: FormatLike, native: Native) -> int:
    if isinstance(value, str):
        return int(native.lib.biosyn_format_from_name(value.encode("ascii")))
    return int(value)


def _spans_from_c(array: Sequence[CSpan], count: int) -> List[Span]:
    return [Span(int(array[i].start), int(array[i].length), int(array[i].class_id)) for i in range(count)]


def _theme_to_c(theme: Optional[ThemeLike], library_path: Optional[str]) -> Tuple[Optional[Sequence[CAnsiStyle]], List[bytes], int]:
    if not theme:
        return None, [], 0
    names = classes(library_path)
    array = (CAnsiStyle * len(theme))()
    strings = []
    for i, (class_ref, sgr) in enumerate(theme.items()):
        class_id = names[class_ref] if isinstance(class_ref, str) else int(class_ref)
        raw_sgr = str(sgr).encode("ascii")
        strings.append(raw_sgr)
        array[i].class_id = class_id
        array[i].reserved = 0
        array[i].ansi_sgr = raw_sgr
    return array, strings, len(theme)


def abi_version(library_path: Optional[str] = None) -> int:
    """Return the loaded C ABI version."""

    return int(load_native(library_path).lib.biosyn_abi_version())


def version(library_path: Optional[str] = None) -> str:
    """Return the loaded libbiosyntax version string."""

    return _decode(load_native(library_path).lib.biosyn_version())


def format_from_name(name: str, library_path: Optional[str] = None) -> Format:
    """Resolve a format name or extension to a ``Format`` enum."""

    value = load_native(library_path).lib.biosyn_format_from_name(name.encode("ascii"))
    return Format(value)


def guess_format_from_path(path: str, library_path: Optional[str] = None) -> Format:
    """Guess a format from a file path or extension."""

    value = load_native(library_path).lib.biosyn_guess_format_from_path(path.encode("utf-8"))
    return Format(value)


def format_name(format: FormatLike, library_path: Optional[str] = None) -> str:
    """Return the canonical C name for a format value."""

    native = load_native(library_path)
    return _decode(native.lib.biosyn_format_name(_coerce_format(format, native)))


def format_count(library_path: Optional[str] = None) -> int:
    """Return the number of built-in format IDs, including ``unknown``."""

    return int(load_native(library_path).lib.biosyn_format_count())


def format_info(format: FormatLike, library_path: Optional[str] = None) -> FormatInfo:
    """Return built-in metadata for one format."""

    native = load_native(library_path)
    raw = CFormatInfo()
    fmt = _coerce_format(format, native)
    ok = native.lib.biosyn_format_info(fmt, ctypes.byref(raw))
    if not ok:
        raise ValueError(f"unknown format: {format!r}")
    return FormatInfo(
        name=_decode(raw.name),
        description=_decode(raw.description),
        stateful=bool(raw.stateful),
    )


def class_name(class_id: ClassLike, library_path: Optional[str] = None) -> str:
    """Return the canonical class name for a token class."""

    return _decode(load_native(library_path).lib.biosyn_class_name(int(class_id)))


def class_scope(class_id: ClassLike, library_path: Optional[str] = None) -> str:
    """Return a TextMate-like scope name for a token class."""

    return _decode(load_native(library_path).lib.biosyn_class_scope(int(class_id)))


def class_ansi_sgr(class_id: ClassLike, library_path: Optional[str] = None) -> str:
    """Return the ANSI SGR fragment used by the sample renderer."""

    return _decode(load_native(library_path).lib.biosyn_class_ansi_sgr(int(class_id)))


def class_default_foreground(class_id: ClassLike, library_path: Optional[str] = None) -> str:
    """Return the built-in theme foreground color as a hex string, or an empty string."""

    return _decode(load_native(library_path).lib.biosyn_class_default_foreground(int(class_id)))


def class_default_background(class_id: ClassLike, library_path: Optional[str] = None) -> str:
    """Return the built-in theme background color as a hex string, or an empty string."""

    return _decode(load_native(library_path).lib.biosyn_class_default_background(int(class_id)))


def class_default_font_style(class_id: ClassLike, library_path: Optional[str] = None) -> str:
    """Return the built-in theme font style, such as ``bold`` or ``italic``."""

    return _decode(load_native(library_path).lib.biosyn_class_default_font_style(int(class_id)))


def class_count(library_path: Optional[str] = None) -> int:
    """Return the number of built-in token classes."""

    return int(load_native(library_path).lib.biosyn_class_count())


def class_info(class_id: ClassLike, library_path: Optional[str] = None) -> ClassInfo:
    """Return all built-in metadata for one token class."""

    raw = CClassInfo()
    ok = load_native(library_path).lib.biosyn_class_info(int(class_id), ctypes.byref(raw))
    if not ok:
        raise ValueError(f"unknown token class: {class_id!r}")
    return ClassInfo(
        name=_decode(raw.name),
        scope=_decode(raw.scope),
        foreground=_decode(raw.foreground),
        background=_decode(raw.background),
        font_style=_decode(raw.font_style),
        ansi_sgr=_decode(raw.ansi_sgr),
    )


def classes(library_path: Optional[str] = None) -> Dict[str, int]:
    """Return a name-to-id map for all built-in token classes."""

    return {
        class_info(class_id, library_path).name: class_id
        for class_id in range(class_count(library_path))
    }


def class_infos(library_path: Optional[str] = None) -> Dict[str, ClassInfo]:
    """Return a name-to-metadata map for all built-in token classes."""

    infos = [class_info(class_id, library_path) for class_id in range(class_count(library_path))]
    return {info.name: info for info in infos}


def formats(library_path: Optional[str] = None) -> Dict[str, Format]:
    """Return a canonical format-name map backed by C introspection."""

    values = range(1, format_count(library_path))
    return {format_info(fmt, library_path).name: Format(fmt) for fmt in values}


def format_infos(library_path: Optional[str] = None) -> Dict[str, FormatInfo]:
    """Return a name-to-metadata map for all known non-unknown formats."""

    infos = [format_info(fmt, library_path) for fmt in range(1, format_count(library_path))]
    return {info.name: info for info in infos}


def highlight_line(
    format: FormatLike,
    line: BytesLike,
    line_no: int = 0,
    max_spans: int = 256,
    library_path: Optional[str] = None,
) -> List[Span]:
    """Highlight one line and return a list of spans.

    ``line_no`` is zero-based and is only used by stateless FASTQ highlighting.
    For FASTQ streams, prefer ``State``.
    """

    native = load_native(library_path)
    fmt = _coerce_format(format, native)
    raw = _as_bytes(line)
    cap = max(1, int(max_spans))

    while True:
        c_spans = (CSpan * cap)()
        required = int(
            native.lib.biosyn_highlight_line_u64(
                fmt,
                raw,
                len(raw),
                int(line_no),
                c_spans,
                cap,
            )
        )
        if required <= cap:
            return _spans_from_c(c_spans, required)
        cap = required


class State:
    """Stateful highlighter.

    Use this for FASTQ and for any streaming workflow where format-specific
    state may matter.
    """

    def __init__(self, format: FormatLike, library_path: Optional[str] = None) -> None:
        self._native = load_native(library_path)
        self._lock = threading.Lock()
        fmt = _coerce_format(format, self._native)
        self._state = self._native.lib.biosyn_state_new(fmt)
        if not self._state:
            raise MemoryError("biosyn_state_new returned NULL")

    def close(self) -> None:
        with self._lock:
            if self._state:
                self._native.lib.biosyn_state_free(self._state)
                self._state = None

    def __enter__(self) -> "State":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

    def highlight_line(self, line: BytesLike, max_spans: int = 256) -> List[Span]:
        raw = _as_bytes(line)
        cap = max(1, int(max_spans))
        with self._lock:
            if not self._state:
                raise RuntimeError("State has been closed")
            while True:
                c_spans = (CSpan * cap)()
                required = int(
                    self._native.lib.biosyn_highlight_next_line_u64(
                        self._state,
                        raw,
                        len(raw),
                        c_spans,
                        cap,
                    )
                )
                if required <= cap:
                    return _spans_from_c(c_spans, required)
                cap = required

    highlight_next_line = highlight_line


def render_ansi_line(
    format: FormatLike,
    line: BytesLike,
    line_no: int = 0,
    spans: Optional[Iterable[Span]] = None,
    theme: Optional[ThemeLike] = None,
    library_path: Optional[str] = None,
) -> str:
    """Render one line with ANSI escape sequences."""

    native = load_native(library_path)
    raw = _as_bytes(line)
    span_list = list(spans) if spans is not None else highlight_line(format, raw, line_no, library_path=library_path)
    c_spans = (CSpan * max(1, len(span_list)))()
    for i, span in enumerate(span_list):
        c_spans[i].start = int(span.start)
        c_spans[i].length = int(span.length)
        c_spans[i].class_id = int(span.class_id)
        c_spans[i].reserved = 0

    count = len(span_list)
    c_theme, _theme_strings, theme_count = _theme_to_c(theme, library_path)
    if theme_count:
        required = int(native.lib.biosyn_render_ansi_line_with_styles_u64(raw, len(raw), c_spans, count, c_theme, theme_count, None, 0))
    else:
        required = int(native.lib.biosyn_render_ansi_line_u64(raw, len(raw), c_spans, count, None, 0))
    out = ctypes.create_string_buffer(required + 1)
    if theme_count:
        native.lib.biosyn_render_ansi_line_with_styles_u64(raw, len(raw), c_spans, count, c_theme, theme_count, out, required + 1)
    else:
        native.lib.biosyn_render_ansi_line_u64(raw, len(raw), c_spans, count, out, required + 1)
    return out.value.decode("utf-8", errors="replace")


def highlight_lines(
    format: FormatLike,
    lines: Iterable[BytesLike],
    stateful: Optional[bool] = None,
    max_spans: int = 256,
    library_path: Optional[str] = None,
) -> Iterator[List[Span]]:
    """Highlight multiple lines.

    Stateful formats such as FASTQ and WIG use ``State`` by default. Pass
    ``stateful=False`` to force stateless line-number based highlighting.
    """

    use_state = format_info(format, library_path).stateful if stateful is None else bool(stateful)
    if use_state:
        with State(format, library_path=library_path) as highlighter:
            for line in lines:
                yield highlighter.highlight_line(line, max_spans=max_spans)
        return

    for line_no, line in enumerate(lines):
        yield highlight_line(format, line, line_no=line_no, max_spans=max_spans, library_path=library_path)


def render_ansi_lines(
    format: FormatLike,
    lines: Iterable[BytesLike],
    stateful: Optional[bool] = None,
    theme: Optional[ThemeLike] = None,
    library_path: Optional[str] = None,
) -> Iterator[str]:
    """Render multiple lines with ANSI escape sequences."""

    use_state = format_info(format, library_path).stateful if stateful is None else bool(stateful)
    if use_state:
        with State(format, library_path=library_path) as highlighter:
            for line in lines:
                yield render_ansi_line(
                    format,
                    line,
                    spans=highlighter.highlight_line(line),
                    theme=theme,
                    library_path=library_path,
                )
        return

    for line_no, line in enumerate(lines):
        yield render_ansi_line(format, line, line_no=line_no, theme=theme, library_path=library_path)


__all__ = [
    "Format",
    "Span",
    "ClassInfo",
    "FormatInfo",
    "State",
    "abi_version",
    "version",
    "format_from_name",
    "guess_format_from_path",
    "format_name",
    "format_count",
    "format_info",
    "class_name",
    "class_scope",
    "class_ansi_sgr",
    "class_default_foreground",
    "class_default_background",
    "class_default_font_style",
    "class_count",
    "class_info",
    "classes",
    "class_infos",
    "formats",
    "format_infos",
    "highlight_line",
    "highlight_lines",
    "render_ansi_line",
    "render_ansi_lines",
]
