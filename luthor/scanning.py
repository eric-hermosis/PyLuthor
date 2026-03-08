from dataclasses import dataclass
from typing import Iterator, Generator 
from luthor.lexing import Lexer

@dataclass(frozen=True)
class Token:
    name : str
    value: str  


class Scanner:

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
    
    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        for line in stream:
            for lexeme in self.lexer.analyze(line):
                yield Token(lexeme.lemma, ''.join(lexeme.words))