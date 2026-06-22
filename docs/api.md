# API Reference

This page summarizes the public Python API.

## Types

### `Format`

`IntEnum` of supported format IDs.

Common values include `Format.FASTA`, `Format.FASTQ`, `Format.SAM`, and
`Format.VCF`. Other values include `Format.BED`, `Format.GTF`, `Format.GFF`,
`Format.PDB`, and `Format.WIG`.

### `Span`

Highlighted byte range.

Attributes:

- `start`: byte offset where the span starts
- `length`: byte length of the span
- `class_id`: token class ID
- `end`: `start + length`

Method:

- `slice(data)`: returns the part of `data` covered by the span

### `ClassInfo`

Token class metadata.

Attributes:

- `name`
- `scope`
- `foreground`
- `background`
- `font_style`
- `ansi_sgr`

### `FormatInfo`

Format metadata.

Attributes:

- `name`
- `description`
- `stateful`

## Version

- `abi_version() -> int`
- `version() -> str`

`version()` returns the bundled `libbiosyntax` version, not the Python package
version.

## Formats

- `format_from_name(name) -> Format`
- `guess_format_from_path(path) -> Format`
- `format_name(format) -> str`
- `format_count() -> int`
- `format_info(format) -> FormatInfo`
- `formats() -> dict[str, Format]`
- `format_infos() -> dict[str, FormatInfo]`

## Token classes

- `class_name(class_id) -> str`
- `class_scope(class_id) -> str`
- `class_ansi_sgr(class_id) -> str`
- `class_default_foreground(class_id) -> str`
- `class_default_background(class_id) -> str`
- `class_default_font_style(class_id) -> str`
- `class_count() -> int`
- `class_info(class_id) -> ClassInfo`
- `classes() -> dict[str, int]`
- `class_infos() -> dict[str, ClassInfo]`

## Highlighting

```python
highlight_line(format, line, line_no=0, max_spans=256) -> list[Span]
```

Highlights one line.

```python
highlight_lines(format, lines, stateful=None, max_spans=256) -> Iterator[list[Span]]
```

Highlights multiple lines.
Stateful formats use `State` by default.
Set `stateful` explicitly to override this.

```python
State(format)
```

Stateful highlighter. Use `highlight_line(line)` on the state object.

## ANSI rendering

```python
render_ansi_line(format, line, line_no=0, spans=None, theme=None) -> str
```

Renders one line with ANSI escape sequences.

```python
render_ansi_lines(format, lines, stateful=None, theme=None) -> Iterator[str]
```

Renders multiple lines with ANSI escape sequences.

`theme` is a mapping from token class name or class ID to an ANSI SGR fragment.
