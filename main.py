from typing import Iterator, Generator
from typing import Sequence
from typing import List
from enum import Enum, auto
from re import Pattern, Match
 
class Category(Enum):
    OPEN   = auto()
    CLOSED = auto()

class Rule:
    word: str
    patterns : List[Pattern[str]]
    category: Category

    def __init__(self, word: str, patterns: Sequence[str], category: Category):
        self.word = word
        self.patterns   = [compile(pattern) for pattern in patterns]
        self.category = category

    def match(self, chunk: str, position: int = 0) -> Match[str] | None:
        for pattern in self.patterns:
            match = pattern.match(chunk, position)
            if match:
                return match
        else:
            return None
    
    def search(self, chunk: str, position: int = 0) -> Match[str] | None:
        for pattern in self.patterns:
            match = pattern.search(chunk, position)
            if match:
                return match
        else:
            return None

class Token:
    name : str
    value: str | None

    def __init__(self, name: str, value: str | None = None):
        self.name  = name
        self.value = value

    def __repr__(self):
        return f"Token({self.name}, {self.value})" if self.value else f"Token({self.name})"

class Scanner:
    def __init__(self, rules: Sequence[Rule]):
        self.rules = rules
        
    def analyze(self, chunk: str) -> Generator[Token, None, None]:
       ... 

    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        for line in stream:
            yield from self.analyze(line)

class Parser:
    ...



from re import compile

if __name__ == '__main__':

    rule = Rule('STAR', [r'(\*\*)(.*?)(\*\*)(?!\*)'], Category.OPEN) 
    match = rule.search("**bold and *italic***") 
    print(match.groups())
    
    rule = Rule('STAR', [r'(\$)(.*?)(\$)'], Category.OPEN)
    pattern = compile(r'(\$)(.*?)(\$)')
    match = rule.search("$E = mc^2$") 
    print(match.groups())

    """
    **bold and *italic***  -> Token(STAR, '**'), Token(TEXT, bold and), Token(STAR, '*'), Token(TEXT, 'italic'), Token(STAR, '*'), Token(STAR, '**')
    **bold and *italic** * -> Token(TEXT, '**bold and * italic), Token(STAR, '**')
    """