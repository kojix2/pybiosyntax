# Usage

Import the package as `biosyntax`:

```python
import biosyntax as bs
```

## Highlight one line

`highlight_line()` returns a list of `Span` objects.
Span offsets and lengths are byte offsets in the input line.

```python
import biosyntax as bs

line = "chr1\t42\trs1\tA\tT\t99\tPASS\n"
spans = bs.highlight_line("vcf", line)

for span in spans:
    print(span.start, span.end, bs.class_name(span.class_id), span.slice(line))
```

`format` can be a format name, an integer format ID, or a `Format` enum value:

```python
bs.highlight_line("vcf", line)
bs.highlight_line(bs.Format.VCF, line)
```

## Highlight multiple lines

Use `highlight_lines()` for an iterable of lines:

```python
lines = [
    "chr1\t42\trs1\tA\tT\t99\tPASS\n",
    "chr2\t99\trs2\tG\tC\t50\tPASS\n",
]

for spans in bs.highlight_lines("vcf", lines):
    print(spans)
```

Stateful formats use a state object by default.
This includes FASTQ and WIG.

## Stateful highlighting

Use `State` directly when you want to control streaming state:

```python
with bs.State("fastq") as state:
    for line in ["@r1\n", "ACGT\n", "+\n", "IIII\n"]:
        spans = state.highlight_line(line)
        print(spans)
```

## ANSI rendering

Use `render_ansi_line()` or `render_ansi_lines()` to produce terminal-colored
text.

```python
rendered = bs.render_ansi_line("vcf", "chr1\t42\trs1\tA\tT\t99\tPASS\n")
print(rendered, end="")
```

You can override ANSI SGR styles by token class name or class ID:

```python
rendered = bs.render_ansi_line(
    "vcf",
    "chr1\t42\trs1\tA\tT\t99\tPASS\n",
    theme={"good": "1;31"},
)
```

## Bytes input

Functions accept `str`, `bytes`, `bytearray`, and `memoryview`.
When the input is `str`, it is encoded as UTF-8 before tokenization.
Span offsets always refer to the encoded bytes.
