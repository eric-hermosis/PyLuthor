from __future__ import annotations
from typing import Iterator, Generator, List
from re import Pattern, compile
from io import StringIO
from collections import deque

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


class Node:
    children: List[Node]
    def __init__(self, name: str, value: str = ""):
        self.name = name
        self.value = value
        self.children = []

    def __repr__(self, level=0) -> str:
        indent = "  " * level
        val = f" {repr(self.value.strip())}" if self.value.strip() else ""
        out = f"{indent}{self.name}{val}\n"
        for child in self.children:
            out += child.__repr__(level + 1)
        return out
    
class Parser:
    def __init__(self): 
        self.queue = deque()
        self.rules = {
            'HEAD':  {'node': 'Header',     'closes_on': ['ENDL']},
            'ITEM':  {'node': 'ListItem',   'closes_on': ['ENDL']},
            'QUOTE': {'node': 'BlockQuote', 'closes_on': ['ENDL']},
            'EMPH':  {'node': 'Emphasis',   'toggle': True},
            'MATH':  {'node': 'MathBlock',  'toggle': True},
            'CODE':  {'node': 'CodeBlock',  'toggle': True},
        }
        self.stack: List[Node] = [Node("DocumentRoot")]

    def parse(self, token: Token) -> Generator[Node, None, None]: 
        self.queue.append(token)
        yield from self._process_queue()

    def flush(self) -> Generator[Node, None, None]: 
        yield from self._process_queue(force_flush=True)

    def _process_queue(self, force_flush: bool = False) -> Generator[Node, None, None]:
        while self.queue:
            token = self.queue.popleft()
             
            if token.name == 'TEXT' and not token.value.strip():
                continue

            current_node = self.stack[-1]
 
            active_rule = next((r for r in self.rules.values() if r.get('node') == current_node.name), None)
            if active_rule and token.name in active_rule.get('closes_on', []):
                finished_node = self.stack.pop()
                if len(self.stack) == 1:
                    yield finished_node
                continue
 
            rule = self.rules.get(token.name)
            
            if rule and rule.get('toggle'):
                if current_node.name == rule['node']:
                    finished_node = self.stack.pop()  
                    if len(self.stack) == 1:
                        yield finished_node
                else:
                    new_node = Node(rule['node'])  
                    current_node.children.append(new_node)
                    self.stack.append(new_node)
                    
            elif rule:
                new_node = Node(rule['node'], token.value)
                current_node.children.append(new_node)
                self.stack.append(new_node)
                
            else: 
                if token.name == 'ENDL' and len(self.stack) == 1:
                    continue  
                    
                leaf = Node(token.name, token.value)
                current_node.children.append(leaf)

        if force_flush:
            while len(self.stack) > 1:
                yield self.stack.pop()


if __name__ == "__main__":
    scanner = Scanner() 
    parser = Parser()
    
    example = StringIO(r"""# Title
Some **bold** and *italic*, inline $E = x**2$ math and a block:

$$
W = x*y + y*z + z*x                       
$$

> This is a blockquote.
- List item 1
- List item 2

Here is some `inline code` and a multi-line script:


```

def hello_world():
print("Hello, World!")

```
""")
    print("--- BUILDING AST ---") 
    for token in scanner.scan(example):
        list(parser.parse(token))
             
    list(parser.flush()) 
    print("--- FULL AST ---")
    print(parser.stack[0])
 