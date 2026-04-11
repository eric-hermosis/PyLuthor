import shutil
from pathlib import Path 
from logging import getLogger
from subprocess import run, DEVNULL, STDOUT, CalledProcessError

from luthor.latex.document import Document
from luthor.processors import CUSTOM_MARKDOWN_TO_LATEX
from luthor.processors.pipeline import Pipeline
from luthor.processors.pandoc import Pandoc 
from luthor.transpiler import Transpiler

logger = getLogger(__name__)

class LatexCompiler:
    def __init__(self, builddir: Path, filename: str) -> None:
        self.builddir = builddir
        self.filename = filename

    def compile(self) -> None:
        logger.info("Compiling PDF and resolving references...")

        try:
            run(
                ["pdflatex", "-interaction=nonstopmode", f"{self.filename}.tex"],
                cwd=self.builddir,
                check=True,
                stdout=DEVNULL,
                stderr=STDOUT,
            )
            logger.debug("First pdflatex pass complete.")

            run(
                ["bibtex", self.filename],
                cwd=self.builddir,
                check=True,
                stdout=DEVNULL,
                stderr=STDOUT,
            )
            logger.info(f"BibTeX processed citations for {self.filename}")

            for pass_num in [2, 3]:
                run(
                    ["pdflatex", "-interaction=nonstopmode", f"{self.filename}.tex"],
                    cwd=self.builddir,
                    check=True,
                    stdout=DEVNULL,
                    stderr=STDOUT,
                )
                logger.debug(f"Pass {pass_num} complete.")

            logger.info(f"Success! Generated {self.builddir / f'{self.filename}.pdf'}")

        except CalledProcessError:
            logger.error("Compilation failed during a subprocess call.")
            logger.error(f"Check {self.builddir / f'{self.filename}.log'} for details.")


class Compiler:
    def __init__(self, filename: str = "output", builddir: str = "build") -> None:
        self.filename = Path(filename).stem
        self.builddir = Path(builddir)
        self.builddir.mkdir(parents=True, exist_ok=True)
 
        self.transpiler = Transpiler()
        self.latex = LatexCompiler(self.builddir, self.filename)

    def compile(self, document: Document) -> None:
        # --- Transpilation phase ---
        for directive in document.forward():
            if directive.name in ["include", "input"]:
                filename = next(iter(directive.arguments[0]))
                source_path = Path(f"{filename}.md")
                output_path = self.builddir / f"{filename}.tex"

                self.transpiler.transpile_file(source_path, output_path)

        # --- Asset copying (still orchestration concern) ---
        assets_src = Path("assets")
        if assets_src.exists():
            shutil.copytree(
                assets_src, self.builddir / "assets", dirs_exist_ok=True
            )
            logger.info("Copied assets to build folder")

        bib_files = list(Path(".").glob("*.bib"))
        for bib in bib_files:
            shutil.copy2(bib, self.builddir / bib.name)
            logger.info(f"Copied bibliography: {bib.name}")

        # --- Write main LaTeX ---
        tex_filepath = self.builddir / f"{self.filename}.tex"
        tex_filepath.write_text(str(document), encoding="utf-8")
        logger.info(f"Saved LaTeX source to {tex_filepath}")

        # --- Compilation phase ---
        self.latex.compile()


    def transpile(self, document: Document) -> Path:
        return self.transpiler.transpile(
            document,
            self.builddir,
            self.filename
        )