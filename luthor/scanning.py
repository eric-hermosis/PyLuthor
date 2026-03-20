from typing import Iterator, Generator
from typing import Sequence 
from typing import List
from re import Pattern, Match 
from re import compile

class Rule:
    name: str
    pattern : Pattern[str]
    terminal: str
    category: str | None

    def __init__(self, name: str, pattern: str, terminal: str, category: str | None = None) -> None:
        self.name = name
        self.pattern  = compile(pattern)
        self.terminal = terminal
        self.category = category

    def match(self, chunk: str, position: int = 0) -> Match[str] | None: 
        return self.pattern.match(chunk, position)  
 
class Token:
    name : str
    value: str | None

    def __init__(self, name: str, value: str | None = None):
        self.name  = name
        self.value = value

    def __repr__(self):
        return f"Token({self.name}, {self.value!r})" if self.value else f"Token({self.name})"
    
class Lexicon:
    rules: List[Rule]

    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = list(rules)

class Scanner:
    def __init__(self, lexicon: Lexicon):
        self.lexicon = lexicon 
        self.state  = None
        self.buffer = [] 

    def flush(self) -> Generator[Token, None, None]:
        if self.buffer: 
            lemma = self.state[0] if self.state else 'TEXT'
            value = ''.join(self.buffer)
            self.buffer.clear()  
            if lemma == 'TEXT' and value.strip() == '':
                return  
            yield Token(lemma, value)

    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        position = 0

        while position < len(chunk):      
            for rule in self.lexicon.rules: 
                if self.state and self.state != (rule.category, rule.terminal):
                    continue

                match = rule.match(chunk, position)
                if match:
                    yield from self.flush()   

                    for group in match.groups():     
                        
                        if group == rule.terminal:
                            yield Token(rule.name, group)  
                            if self.state and self.state == (rule.category, rule.terminal):
                                self.state = None   
                                
                            elif not self.state and rule.category:
                                self.state = (rule.category, rule.terminal)
 
                        elif rule.category: 
                            self.state = (rule.category, rule.terminal)
                            yield Token(rule.category, group)  

                        else:
                            yield from self.analyze(group)

                    position = match.end()
                    break
            else: 
                self.buffer.append(chunk[position])
                position+=1 

        if not self.state:
            yield from self.flush()

    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        for line in stream: 
            yield from self.analyze(line) 