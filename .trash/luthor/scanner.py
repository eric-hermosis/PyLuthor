from typing import Generator
from typing import Iterator
from luthor.lexicon import Lexicon

class Token:
    name: str
    value: object

    def __init__(self, name: str, value: object) -> None:
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.name}, {self.value!r})" if self.value else f"Token({self.name})" 
    
    def __eq__(self, other: object) -> bool:
            if not isinstance(other, Token):
                return False
            return self.name == other.name and self.value == other.value
    
class Scanner:
    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon
        self.cursor = 0
        self.buffer: list[str] = []
        self.state: str | None = None

    def flush(self) -> Generator[Token, None, None]:
        if self.buffer:
            yield Token(self.state or '<|TEXT|>', ''.join(self.buffer))
            self.buffer.clear()
 
    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        self.cursor = 0
        while self.cursor < len(chunk):
            for rule in self.lexicon.rules:
                match = rule.match(chunk, self.cursor)
                if match:
                    if self.state and self.state == rule.content:
                        yield from self.flush()
                        yield Token(str(rule.terminal), match.group())
                        self.cursor = match.end() 
                        self.state = None
                        break
                    elif self.state:
                        self.push(chunk[self.cursor])
                        break
                    else:
                        yield from self.flush()
                        yield Token(str(rule.terminal), match.group())
                        self.cursor = match.end() 
                        self.state = rule.content
                        break
            else:
                self.push(chunk[self.cursor])

    def push(self, char: str) -> None:
        self.buffer.append(char)
        self.cursor += 1 

    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        for line in stream:
            yield from self.analyze(line)
        yield from self.flush()  