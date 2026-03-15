from typing import Iterator, Generator
from luthor.lexing import Lexicon

class Token:

    def __init__(self, type: str, value: str) -> None:
        self.type  = type
        self.value = value


class Scanner:
    
    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon

    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        ...

    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        ...