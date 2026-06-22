# Command Line

pybiosyntax installs a small command line program named `biosyntax`.

## Basic usage

```sh
biosyntax sample.vcf
```

The command guesses the format from the file name when possible.
It writes ANSI-colored text to standard output.

## Specify a format

Use `--format` or `-f` when the format cannot be guessed from the file name:

```sh
biosyntax --format fastq reads.txt
biosyntax -f vcf variants.txt
```

## Read from standard input

Pass `-` or omit the path to read from standard input:

```sh
cat sample.vcf | biosyntax --format vcf
biosyntax --format sam < alignments.sam
```

## Module form

The CLI can also be run as a Python module:

```sh
python -m biosyntax sample.vcf
python -m biosyntax --format fastq reads.fastq
```

## Supported formats

Supported names include:

- `fasta`
- `fastq`
- `sam`
- `vcf`
- `bed`
- `gtf`
- `gff`
- `pdb`
- `clustal`
- `faidx`
- `flagstat`
- `wig`
- `fasta-nt`
- `fasta-hc`
- `fasta-clustal`
- `fasta-hydro`
- `fasta-taylor`
- `fasta-zappo`
- `fasta-orf`
