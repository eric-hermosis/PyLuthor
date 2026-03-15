from __future__ import annotations
from uuid import uuid4
from typing import Sequence
from pathlib import Path
from luthor.markdown.parser import Parser

class Node:
    def __init__(
        self,   
        children: Sequence[Node] | None = None
    ) -> None:
        self.id = uuid4()   
        self.children = list(children) if children else []

    def dump(self) -> str:
        """Recursively renders the node and its children into a LaTeX string."""
        return "\n".join(child.dump() for child in self.children if child is not None)
 
class Document:
    def __init__(
        self,
        preamble: Sequence[Node] | None = None,
        body: Sequence[Node] | None = None
    ) -> None:
        self.preamble_root = Node(preamble) if preamble else Node([])
        self.body_root = Node(body) if body else Node([])

    def dump(self) -> str: 
        preamble_str = self.preamble_root.dump() 
        body_str = self.body_root.dump()
         
        return f"{preamble_str}\n\\begin{{document}}\n\\maketitle\n{body_str}\n\\end{{document}}"

class Command(Node):
    def __init__(
        self,
        name: str,
        arguments: Sequence[str] | None = None,
        options: Sequence[str] | str | None = None, 
    ) -> None:
        super().__init__()
        self.name = name
        self.arguments = list(arguments) if arguments else []
         
        if isinstance(options, str):
            self.options = [options]
        else:
            self.options = list(options) if options else [] 

    def dump(self) -> str:
        cmd = f"\\{self.name}"
         
        if self.options:
            opts = ",".join(self.options)
            cmd += f"[{opts}]"
             
        if self.arguments:
            for arg in self.arguments:
                cmd += f"{{{arg}}}"
                
        return cmd

class Geometry(Node):
    def __init__(
        self,
        paper: str = "a4paper",
        top: str | None = None,
        bottom: str | None = None,
        left: str | None = None,
        right: str | None = None,
    ) -> None:
        super().__init__()
        self.paper = paper
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def dump(self) -> str: 
        config = [self.paper]
        
        if self.top: config.append(f"top={self.top}")
        if self.bottom: config.append(f"bottom={self.bottom}")
        if self.left: config.append(f"left={self.left}")
        if self.right: config.append(f"right={self.right}")
            
        opts = ",".join(config)
        return f"\\geometry{{{opts}}}" 
        
class Include(Node):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename
        self.parser = Parser()
        
    def dump(self) -> str:  
        file_path = Path(self.filename)
        if not file_path.suffix:
            file_path = file_path.with_suffix(".md")
            
        if not file_path.exists():
            return f"% ERROR: File {file_path} not found."
             
        text = file_path.read_text(encoding="utf-8") 
        return self.parser.markdown_to_latex(text)
    
class Bibliography(Node):
    def __init__(self, file: str, style: str = "unsrt") -> None:
        super().__init__()
        self.file = file
        self.style = style

    def dump(self) -> str:  
        return (
            "\\newpage\n"
            f"\\bibliographystyle{{{self.style}}}\n"
            f"\\bibliography{{{self.file}}}"
        )