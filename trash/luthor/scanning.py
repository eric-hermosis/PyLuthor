from typing import Iterator, Generator  
from luthor.lexing import Lexicon

class Token:
    name: str
    value: str | None

    def __init__(self, name: str, value: str | None = None):
        self.name = name
        self.value = value 

    def __repr__(self) -> str:
        if self.value is None:
            return f"Token({self.name})"
        else:
            return f"Token({self.name!r}, {self.value!r})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return self.name == other.name and self.value == other.value

    def __ne__(self, other) -> bool:
        return not self == other
        

class Scanner:    
    def __init__(self, lexicon: Lexicon):
        self.lexicon = lexicon
        self.buffer  = []
        self.mode    = None

    def flush(self) -> Generator[Token, None, None]:
        if self.buffer:
            yield Token('CONTENT', ''.join(self.buffer))
            self.buffer.clear()

    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        position = 0
        while position < len(chunk):
            for rule in self.lexicon.rules:
                match = rule.match(chunk, position)
                if match: 
                    yield from self.flush() 
                    yield Token(rule.lemma, match.group())
                    position = match.end()
                    break
            else:
                self.buffer.append(chunk[position])
                position += 1 
        yield from self.flush()

    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        for line in stream:
            yield from self.analyze(line)