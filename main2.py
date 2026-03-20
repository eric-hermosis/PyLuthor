from __future__ import annotations

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
        return f"Token({self.name}, {self.value})" if self.value else f"Token({self.name})"

class Scanner:
    def __init__(self, rules: Sequence[Rule]):
        self.rules  = rules
        self.state  = None
        self.buffer = [] 

    def flush(self) -> Generator[Token, None, None]:
        if self.buffer: 
            token_name = self.state[0] if self.state else 'TEXT'
            yield Token(token_name, ''.join(self.buffer))
            self.buffer.clear()
        
    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        position = 0

        while position < len(chunk):      
            for rule in self.rules: 
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
            line = line.rstrip()
            yield from self.analyze(line) 
 

class Node:
    kind:  str
    value: str | None
    children: List[Node]

    def __init__(self, kind: str, value: str | None = None):
        self.kind = kind
        self.value = value
        self.children = [] 

    def __repr__(self, level=0) -> str:
        indent = "  " * level
        if self.value is not None:
            return f"{indent}{self.kind}({repr(self.value)})"
        
        res = f"{indent}{self.kind}\n"
        for child in self.children:
            res += child.__repr__(level + 1) + "\n"
        return res.rstrip()

    def link(self, node: Node):
        self.children.append(node) 
        
class Parser:
    def __init__(self, delimiters: dict[tuple[str, str], str], content: dict[str, str]): 
        self.delimiters = delimiters 
        self.content = content

    def parse(self, tokens: Iterator[Token]) -> Node:
        root = Node('Document') 
        stack: list[tuple[tuple[str, str | None] | None, Node]] = [(None, root)]

        for token in tokens:
            sig = (token.name, token.value) 
            if sig in self.delimiters:
                active_sigs = [s for s, _ in stack]
                
                if sig in active_sigs: 
                    while stack:
                        popped_sig, node = stack.pop()
                        if popped_sig == sig: 
                            stack[-1][1].link(node)
                            break
                        else: 
                            stack[-1][1].link(node)
                else: 
                    node_type = self.delimiters[sig]
                    stack.append((sig, Node(node_type)))
             
            else:
                node_type = self.content.get(token.name, 'Text') 
                stack[-1][1].link(Node(node_type, token.value))
 
        while len(stack) > 1:
            _, node = stack.pop()
            stack[-1][1].link(node)
 
        return root


from io import StringIO

if __name__ == '__main__':

    example = StringIO(r"""
This is an example with **bold and *italic***, inline math like $f(x) = x**2$ and math blocks:
                       
$$
f(x,y,z) = x*y + y*z + z*x                       
$$

""") 
    scanner = Scanner([ 
        Rule('STAR', r'(\*\*)(.*?)(\*\*)(?!\*)', '**'),
        Rule('STAR', r'(\*)(.*?)(\*)', '*'),
        Rule('SIGN', r'(\$\$)', '$$' ,'MATH'),
        Rule('SIGN', r'(\$)(.*?)(\$)', '$' ,'MATH'), 
    ])
    
    parser = Parser(
        delimiters={
            ('STAR', '**'): 'Bold',
            ('STAR', '*'):  'Italic',
            ('SIGN', '$$'): 'Math[Block]',
            ('SIGN', '$'):  'Math[Inline]'
        },

        content={
            'TEXT': 'Text',
            'MATH': 'Math[Content]'
        }
    )

    tokens = scanner.scan(example)
    ast = parser.parse(tokens)
    print(ast)