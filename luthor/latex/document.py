from __future__ import annotations
from typing import Protocol
from typing import Generator
from typing import Sequence
from typing import List
from luthor.latex.command import Command

class Directive(Protocol):
    name: str

    def forward(self) -> Generator[Command, None, None]:
        ...

class Document:
    preamble: List[Directive]
    body: List[Directive]

    def __init__(self, preamble: Sequence[Directive] | None = None, body: Sequence[Directive] | None = None) -> None:
        self.preamble = list(preamble) if preamble else []
        self.body = list(body) if body else []

    def forward(self) -> Generator[Command, None, None]:
        for directive in self.preamble:
            yield from directive.forward()    
        yield Command("begin", {"document"})

        for directive in self.body:
            yield from directive.forward()    
        yield Command("end", {"document"})

    def __str__(self) -> str:
        lines = [] 
        for directive in self.preamble:
            lines.append(str(directive))
             
        lines.append("\n\\begin{document}")
         
        for directive in self.body:
            lines.append(str(directive))
             
        lines.append("\\end{document}\n") 
        return "\n".join(lines)
