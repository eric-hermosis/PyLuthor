from luthor.processors import CUSTOM_MARKDOWN_TO_LATEX
from luthor.processors import Pipeline
from luthor.processors.pandoc import Pandoc

def test_markdown_to_latex(markdown, latex):
    pipeline = Pipeline([CUSTOM_MARKDOWN_TO_LATEX, Pandoc('markdown', 'latex')])
    assert latex == pipeline.process(markdown)