from pathlib import Path
from logging import getLogger
from luthor.latex.document import Document
from luthor.processors import CUSTOM_MARKDOWN_TO_LATEX
from luthor.processors.pipeline import Pipeline
from luthor.processors.pandoc import Pandoc

logger = getLogger(__name__)

class Transpiler:
    def __init__(self) -> None:
        self.pipeline = Pipeline([CUSTOM_MARKDOWN_TO_LATEX, Pandoc()])

    def transpile_file(self, source_path: Path, output_path: Path) -> None:
        if not source_path.exists():
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)

        text = source_path.read_text(encoding="utf-8")
        tex_content = self.pipeline.process(text)
        output_path.write_text(tex_content, encoding="utf-8")
        logger.info(f"Compiled include: {source_path} -> {output_path}")
 

    def transpile(self, document: Document, builddir: Path, filename: str) -> Path:
        builddir.mkdir(parents=True, exist_ok=True)

        for directive in document.forward():
            if directive.name in ["include", "input"]:
                name = next(iter(directive.arguments[0]))

                source_path = Path(f"{name}.md")
                output_path = builddir / f"{name}.tex"

                self.transpile_file(source_path, output_path)

        tex_filepath = builddir / f"{Path(filename).stem}.tex"
        tex_filepath.write_text(str(document), encoding="utf-8")
        logger.info(f"Saved LaTeX source to {tex_filepath}")
        return tex_filepath