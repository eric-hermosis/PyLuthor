import shutil
from pathlib import Path 
from logging import getLogger
from subprocess import run, DEVNULL, STDOUT, CalledProcessError

from luthor.latex.document import Document
from luthor.processors import CUSTOM_MARKDOWN_TO_LATEX
from luthor.processors.pipeline import Pipeline
from luthor.processors.pandoc import Pandoc 
  
logger = getLogger(__name__)

class Compiler: 
    def __init__(self, filename: str = "output", builddir: str = "build") -> None: 
        self.filename = Path(filename).stem 
        self.builddir = Path(builddir)   
        self.builddir.mkdir(parents=True, exist_ok=True)    
        self.pipeline = Pipeline([CUSTOM_MARKDOWN_TO_LATEX, Pandoc()]) 
        
    def compile(self, document: Document) -> None:  
        for directive in document.forward():
            if directive.name in ['include', 'input']:
                filename = next(iter(directive.arguments[0])) 
                source_path = Path(f"{filename}.md")
                output_path = self.builddir / f"{filename}.tex"
                
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                if source_path.exists():
                    text = source_path.read_text(encoding='utf-8')
                    tex_content = self.pipeline.process(text)
                    output_path.write_text(tex_content, encoding='utf-8')
                    logger.info(f"Compiled include: {source_path} -> {output_path}")
 
        assets_src = Path("assets")
        if assets_src.exists():
            shutil.copytree(assets_src, self.builddir / "assets", dirs_exist_ok=True)
            logger.info("Copied assets to build folder")
 
        bib_files = list(Path(".").glob("*.bib"))
        for bib in bib_files:
            shutil.copy2(bib, self.builddir / bib.name)
            logger.info(f"Copied bibliography: {bib.name}")
  
        tex_filepath = self.builddir / f"{self.filename}.tex"
        tex_filepath.write_text(str(document), encoding="utf-8")
        logger.info(f"Saved LaTeX source to {tex_filepath}")  
 
        logger.info("Compiling PDF and resolving references...")
        try:  
            run(["pdflatex", "-interaction=nonstopmode", f"{self.filename}.tex"],
                cwd=self.builddir, check=True, stdout=DEVNULL, stderr=STDOUT)
            logger.debug("First pdflatex pass complete.")
 
            run(["bibtex", self.filename], 
                cwd=self.builddir, check=True, stdout=DEVNULL, stderr=STDOUT)
            logger.info(f"BibTeX processed citations for {self.filename}")
 
            for pass_num in [2, 3]:
                run(["pdflatex", "-interaction=nonstopmode", f"{self.filename}.tex"],
                    cwd=self.builddir, check=True, stdout=DEVNULL, stderr=STDOUT)
                logger.debug(f"Pass {pass_num} complete.")
                
            logger.info(f"Success! Generated {self.builddir / f'{self.filename}.pdf'}")
            
        except CalledProcessError as e: 
            logger.error(f"Compilation failed during a subprocess call.")
            logger.error(f"Check {self.builddir / f'{self.filename}.log'} for details.")