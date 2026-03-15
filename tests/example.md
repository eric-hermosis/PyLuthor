# PyLuthor

**PyLuthor** is a Python package for compiling Markdown into structured output formats. It is designed to be lightweight, extensible, and suitable for embedding in documentation pipelines or custom static site workflows.

This document is an example Markdown file used for **testing the PyLuthor Markdown compiler itself**. It intentionally includes a variety of Markdown constructs to validate parsing, rendering, and edge-case handling.

## Features

PyLuthor aims to support a modern Markdown workflow with:

- Standard Markdown syntax
- Code blocks and syntax highlighting
- Tables
- Nested lists
- Inline formatting
- Extensible plugin architecture
- Mathematical expressions
 

## Basic Formatting

You can use standard inline formatting:

- **Bold text**
- *Italic text* 
 

## Math Examples

PyLuthor may optionally support LaTeX-style math rendering.

### Inline Math

Einstein's famous equation: $E = mc^2$.

Another example: $a^2 + b^2 = c^2$.

### Block Math

$$
\int_0^1 x^2 \, dx = \frac{1}{3}
$$

Quadratic formula:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

A summation example:

$$
\sum_{i=1}^{n} i = \frac{n(n+1)}{2}
$$
 

## Lists

### Unordered

- Item one
- Item two
  - Nested item
  - Another nested item
- Item three

### Ordered

1. First step
2. Second step
3. Third step
 