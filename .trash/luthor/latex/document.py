from __future__ import annotations
from typing import Protocol
from typing import Generator
from typing import Sequence
from typing import List

class Directive(Protocol):
    
    def forward(self) -> Generator[Directive, None, None]: 
        ...

class Document:
    preamble: List[Directive]
    body: List[Directive]

    def __init__(self, preamble: Sequence[Directive] | None = None, body: Sequence[Directive] | None = None) -> None:
        self.preamble = list(preamble) if preamble else []
        self.body = list(body) if body else []