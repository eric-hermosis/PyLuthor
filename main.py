from typing import Generator
from typing import Sequence, List 
from re import Pattern, Match

class Lexeme:
    lemma: str 
    match: str | Match[str]

    def __init__(self, lemma: str, match: str | Match[str]):
        self.lemma = lemma
        self.match = match

class Rule:
    name: str 

    def __init__(self, pattern: Pattern[str], name: str):
        self.pattern = pattern
        self.name    = name 

    def search(self, chunk: str) -> Lexeme:
        match = self.pattern.search(chunk)
        return Lexeme(self.name, match) if match else None

    def match(self, chunk: str, position: int) -> Lexeme | None:
        match = self.pattern.match(chunk, position)
        return Lexeme(self.name, match) if match else None

class Lexicon:
    rules: List[Rule]

    def __init__(self, rules: Sequence[Rule]):
        self.rules = list(rules)
        

class Lexer:    
    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon
        self.buffer  = []  
        self.state   = None

    def flush(self) -> Generator[Lexeme, None, None]:
        if self.buffer:
            yield Lexeme(self.state or 'CONTENT', ''.join(self.buffer))
            self.buffer.clear()

    def analyze(self, chunk: str) -> Generator[Lexeme, None, None]:
        position = 0
        while position < len(chunk): 
            for rule in self.lexicon.rules:
                lexeme = rule.match(chunk, position)
                if lexeme:
                    yield from self.flush()
                    yield lexeme
                    position = lexeme.match.end()
                    break
                
            else:
                self.buffer.append(chunk[position])
                position+=1
        yield from self.flush()

from io import StringIO
from re import compile

if __name__ == '__main__': 
    lexicon = Lexicon([
        Rule(compile(r'^#{1,6}'), 'HASHTAG'),
        Rule(compile(r'\${1,2}'), 'DOLLARS'),
        Rule(compile(r'\n$')    , 'NEWLINE')
    ])

    example = StringIO(r"""
### Title
$$
w = x*y + y*z + z*x
$$
"""
)
    lexer = Lexer(lexicon)
    for line in example:
        for lexeme in lexer.analyze(line):
            print(lexeme.lemma, lexeme.match)