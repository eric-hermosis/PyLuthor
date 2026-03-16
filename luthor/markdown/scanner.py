from typing import Iterator, Generator
from re import Pattern, compile 

class Token:
    name: str
    value: str

    def __init__(self, name: str, value: str) -> None:
        self.name  = name.strip() 
        self.value = value
        
    def __repr__(self) -> str: 
        return f"Token({self.name}, {repr(self.value)})"
 

class Rule:
    def __init__(self, name: str, pattern: Pattern[str], state: str = None):
        self.name = name
        self.pattern = pattern
        self.state = state

class Scanner:
    def __init__(self): 
        self.rules = [
            Rule('CODE ', compile(r'^`+')      ,'CODE'), 
            Rule('HEAD' , compile(r'^#{1,6}\s'), None),
            Rule('QUOTE', compile(r'^>\s?')    , None),
            Rule('ITEM' , compile(r'^-\s')     , None),
            Rule('MATH' , compile(r'\${1,2}')  ,'MATH'),
            Rule('EMPH' , compile(r'\*{1,2}')  , None),
            Rule('ENDL' , compile(r'\n')       , None)
        ]
        self.buffer = []
        self.state  = None

    def flush(self, explicit_name: str = None) -> Generator[Token, None, None]:
        if self.buffer: 
            name = explicit_name if explicit_name else (self.state or 'TEXT')
            yield Token(name, ''.join(self.buffer))
            self.buffer.clear()

    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        position = 0
        while position < len(chunk): 
            match_found = False
            for rule in self.rules:
                match = rule.pattern.match(chunk, position)
                if match:  
                    if self.state and rule.state == self.state: 
                        yield from self.flush(f"{self.state}_CONTENT")
                        yield Token(rule.name, match.group(0))
                        self.state = None
                        position = match.end()
                        match_found = True
                        break
                      
                    if not self.state:
                        yield from self.flush('TEXT')
                        yield Token(rule.name, match.group(0))
                        self.state = rule.state
                        position = match.end()
                        match_found = True
                        break
                         
            if not match_found:
                self.buffer.append(chunk[position])
                position += 1
 
        if not self.state:
            yield from self.flush('TEXT')

    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        for line in stream:
            yield from self.analyze(line) 
        yield from self.flush()