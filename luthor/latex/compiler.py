import subprocess
from pathlib import Path
from luthor.latex.nodes import Document

class Compiler:
    def __init__(self, output_path: str | Path) -> None:
        self.output_path = Path(output_path).resolve()

    def compile(self, document: Document) -> None: 
        latex_content = document.dump()
 
        self.output_path.write_text(latex_content, encoding="utf-8")
        print(f"Generated {self.output_path}")
 
        working_dir = self.output_path.parent
        filename = self.output_path.name
        stem = self.output_path.stem 
        cmds = [
            ["pdflatex", filename],
            ["bibtex", stem],
            ["pdflatex", filename],
            ["pdflatex", filename],
        ]
 
        try:
            for cmd in cmds: 
                subprocess.run(cmd, cwd=working_dir, check=True)
                
            print(f"Successfully generated PDF: {self.output_path.with_suffix('.pdf')}")
            
        except subprocess.CalledProcessError as e:
            print(f"Error during compilation: {e}")
            print("Check the .log file for specific LaTeX errors.")