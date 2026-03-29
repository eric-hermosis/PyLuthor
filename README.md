# Luthor

**Luthor** is a Pythonic bridge for generating I made to compile my markdown files into pdf without
wrestling with `pdflatex` CLI and pandoc. 

## Installation

```bash
pip install luthor
```
*(Note: Till I build a full compiler you need pandoc and a latex compiler)*

## Quick Start

Separate your document configuration (Python) from your content (Markdown).

### Define the Document Structure
Use the `Document` class to set up your packages and document metadata.

```python
from luthor.latex.document import Document, Command  
from luthor.compiler import Compiler

document = Document(
    preamble=[  
        Command("documentclass", ["12pt"], {"article"}),
        Command("usepackage", ["spanish"], {"babel"}),
        Command("title", {"Markdown Example"}),
        Command("author", {"Eric Hermosis"}),
    ], 
    body=[
        Command("maketitle"),  
        Command("include", {"README"}), #  wherever your .md files are.
        Command("bibliography", {"references"}) 
    ]
) 

compiler = Compiler(filename="output.pdf", builddir="build") 
compiler.compile(document)
```