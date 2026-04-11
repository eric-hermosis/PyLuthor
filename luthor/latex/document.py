from __future__ import annotations
from typing import Protocol
from typing import Generator
from typing import Sequence
from typing import List
from typing import Tuple 
from luthor.latex.command import Command

class Directive(Protocol):
    name: str

    def forward(self) -> Generator[Command, None, None]:
        ...

class Document:
    preamble: List[Directive]
    body: List[Directive]

    def __init__(self, preamble: Sequence[str | Tuple | Directive] | None = None, body: Sequence[str | Tuple | Directive] | None = None) -> None:
        self.preamble = []
        for directive in preamble or []:
            if isinstance(directive, str):
                self.preamble.append(Command(directive))
            elif isinstance(directive, tuple):
                self.preamble.append(Command(*directive))
            elif isinstance(directive, Command):
                self.preamble.append(directive)
            else:
                raise TypeError(f"Expected a tuple or Command, got {type(directive).__name__}")

        self.body = []
        for directive in body or []:
            if isinstance(directive, str):
                self.body.append(Command(directive))
            elif isinstance(directive, tuple):
                self.body.append(Command(*directive))
            elif isinstance(directive, Command):
                self.body.append(directive)
            else:
                raise TypeError(f"Expected a tuple or Command, got {type(directive).__name__}")

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
