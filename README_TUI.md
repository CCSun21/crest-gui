# CREST TUI

A Terminal User Interface for the [CREST](https://github.com/grimme-lab/crest) computational chemistry tool, built with Python and [Textual](https://textual.textualize.io/).

## Features

- **10 workflow screens**: iMTD-GC conformer search, entropy/thermodynamics, constrained search, protonation/deprotonation, NCI complex search, QCG solvation, MS/React pathways, structure optimization, molecular dynamics, CREGEN ensemble sorting
- **Live preview**: Instantly generates TOML input files and CLI commands as you fill in parameters
- **Job monitor**: Streams CREST output in real time with cancel support
- **Settings**: Persist CREST/xtb binary paths, thread count, default method, and theme
- **Widgets**: Structure viewer, ensemble browser, ASCII energy bar chart, constraint editor, file picker

## Installation

```bash
pip install -e ".[dev]"
```

Requires Python ≥ 3.10 and a working `crest` binary in `$PATH`.

## Usage

```bash
crest-tui
# or
python -m crest_tui
```

### Key bindings

| Key        | Action        |
|------------|---------------|
| `Ctrl+D`   | Dashboard     |
| `Ctrl+S`   | Settings      |
| `Ctrl+J`   | Job monitor   |
| `Ctrl+Q`   | Quit          |
| `Escape`   | Back / pop screen |

## Running tests

```bash
pytest tests/ -v
```

## Directory layout

```
crest_tui/
├── app.py              # Main Textual App
├── config.py           # AppConfig dataclass + load/save
├── toml_builder.py     # CREST 3.0 TOML input builders
├── command_builder.py  # CLI command builders
├── runner.py           # Async job runner
├── parser.py           # CREST output parsers
├── screens/            # One module per workflow screen
├── widgets/            # Reusable TUI widgets
└── styles/
    └── crest.tcss      # Textual CSS
```
