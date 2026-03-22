from __future__ import annotations

from pathlib import Path
from typing import Generator, Iterator
from typing import Dict
from re import Pattern, Match
from re import compile
   
class Token:
    name : str
    value: str | None

    def __init__(self, name: str, value: str | None = None):
        self.name  = name
        self.value = value

    def __repr__(self):
        return f"Token({self.name}, {self.value!r})" if self.value else f"Token({self.name})"
 

class Rule: 
    pattern: Pattern[str] 
    content: str | None

    def __init__(self, pattern: str, content: str | None = None) -> None:
        self.pattern = compile(pattern) 
        self.content = content

    def match(self, chunk: str, position: int) -> Match[str] | None:
        return self.pattern.match(chunk, position)
    
 
class Lexicon:
    rules: Dict[str, Rule]

    def __init__(self, rules: Dict[str, Rule]) -> None:
        self.rules = rules 


class Scanner:

    def __init__(self, lexicon: Lexicon) -> None: 
        self.lexicon = lexicon
        self.buffer  = []


    def flush(self) -> Generator[Token, None, None]:
        if self.buffer:
            yield Token('TEXT', ''.join(self.buffer))
            self.buffer.clear()


    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        position = 0
        while position < len(chunk):
            for terminal, rule in self.lexicon.rules.items():
                match = rule.match(chunk, position)
                if match:
                    yield from self.flush()
                    yield Token(terminal, match.group())
                    position = match.end()
                    break

            else:
                self.buffer.append(chunk[position])
                position += 1

        yield from self.flush() 


    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        for line in stream:
            yield from self.analyze(line)


from collections import deque
from typing import Sequence
from typing import List

class Node:
    kind:  str 
    children: List[Node]

    def __init__(self, kind: str, value: str | None = None):
        self.kind = kind
        self.value = value
        self.children = [] 

    def __repr__(self, level: int = 0) -> str:
        indent = "  " * level
        if self.value is not None:
            return f"{indent}{self.kind}" 
        representation = f"{indent}{self.kind}\n"
        for child in self.children:
            representation += child.__repr__(level + 1) + "\n"
        return representation.rstrip()

    def link(self, node: Node):
        self.children.append(node) 

class Production:
    head: str
    body: List[str]

    def __init__(self, head: str, body: Sequence[str]) -> None:
        self.head = head
        self.body = list(body) 

class Grammar:
    def __init__(self, productions: Sequence[Production]) -> None:
        self.productions = productions

class Parser: 
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self.tokens = deque[Token]()
        self.cursor = 0

    def push(self, token: Token) -> None:
        self.tokens.append(token) 
     
    def parse(self) -> Generator[Node, None, None]:
        while self.cursor < len(self.tokens):
            yield Node('TEXT') 

class Include:
    node: Node

    @staticmethod
    def find(filename: str) -> Path:
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix('.md')
        if not path.exists():
            raise Exception(f"ERROR: File {path} not found.")
        return path

    def __init__(self, filename: str) -> None:
        self.path = self.find(filename) 
    
        self.scanner = Scanner(Lexicon({
            'STAR': Rule(r'\*')
        }))

        self.parser = Parser(Grammar([ 
            Production('Bold',   ['STAR','STAR','CONTENT','STAR','STAR']),
            Production('Italic', ['STAR','CONTENT','STAR']), 
        ]))

    def parse(self): 
        with self.path.open(encoding='utf-8') as file:
            for token in self.scanner.scan(file):
                self.parser.push(token)

    
if __name__ == '__main__':
    include = Include('example')
    node = include.parse()
    print(node) 


