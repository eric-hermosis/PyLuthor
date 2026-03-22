from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
from typing import Generator
from typing import List
from typing import Sequence
from collections import deque

class Token:
    name : str
    value: str

    def __init__(self, name: str, value: str) -> None:
        self.name  = name
        self.value = value

    def __repr__(self):
        return f"Token({self.name}, {self.value!r})" if self.value else f"Token({self.name})"

@dataclass
class Node:
    kind: str
    value: Optional[str] = None
    metadata: Dict[str, str] | None = None
    children: List[Node] | None = None 

    def __repr__(self, level: int = 0) -> str:
        pad = "  " * level
        extra = []
        if self.value is not None:
            extra.append(repr(self.value))
        if self.metadata:
            extra.append(repr(self.metadata))
        head = self.kind if not extra else f"{self.kind}(" + ", ".join(extra) + ")"
        if not self.children:
            return pad + head
        out = [pad + head]
        for child in self.children:
            out.append(child.__repr__(level + 1))
        return "\n".join(out)
    
class Production:
    head: str
    body: List[str]
    build: Callable[[Sequence[Token]], Node]

    def __init__(self, head: str, body: Sequence[str], builder: Callable | None = None) -> None:
        self.head = head
        self.body = list(body)
        self.build = builder or (
            lambda chunk: Node(
                self.head, 
                value=''.join(token.value for token in chunk if token.name == 'TEXT')
            )
        )
        
    @property
    def is_recursive(self) -> bool:
        return 'CONTENT' in self.body

    @property
    def opener(self) -> list[str]:
        if 'CONTENT' not in self.body:
            return self.body
        index = self.body.index('CONTENT')
        return self.body[:index]

    @property
    def closer(self) -> list[str]:
        if 'CONTENT' not in self.body:
            return []
        index = self.body.index('CONTENT')
        return self.body[index + 1:]
    
    def match(self, tokens: Sequence[Token]) -> bool:
        if len(tokens) < len(self.body):
            return False
        return all(tokens[index].name == self.body[index] for index in range(len(self.body))) 

    def opens(self, tokens: Sequence[Token]) -> bool:
        if len(tokens) < len(self.opener):
            return False
        return all(tokens[index].name == self.opener[index] for index in range(len(tokens))) 


@dataclass
class Grammar:
    productions: list[Production]

    @property
    def recursions(self) -> list[Production]:

        return sorted(
            [production for production in self.productions if production.is_recursive],
            key=lambda production: len(production.opener),
            reverse=True
        )

    @property
    def terminals(self) -> list[Production]:
        return sorted(
            [production for production in self.productions if not production.is_recursive],
            key=lambda production: len(production.body),
            reverse=True
        ) 

class Parser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar 
        self.tokens  = deque[Token]() 

    def push(self, token: Token) -> None:
        self.tokens.append(token)

    def flush(self) -> Generator[Node, Any, None]:  
        yield from self.parse()  
    
    def repeated(self) -> Generator[Token, None, None]:
        position = 0
        terminal = self.tokens[0].name
        while position < len(self.tokens) and self.tokens[position].name == terminal:
            yield self.tokens[position]
            position += 1

    def consume(self, positions: int) -> List[Token]:  
        return [self.tokens.popleft() for _ in range(positions)] 

    def parse(self, closing: tuple[str,int] | None = None) -> Generator[Node, None, None]: 

        while self.tokens:    
        
            repeated = list(self.repeated())
            terminal = self.tokens[0].name  

            if closing and closing == (terminal, len(repeated)): 
                self.consume(len(repeated))
                break
 
            for production in self.grammar.recursions:  
                if production.opens(repeated): 
                    chunk = self.consume(len(production.opener))  
                    inner = self.parse(closing=(terminal, len(production.closer)))
                    yield Node(production.head, children=list(inner)) 
                    break
            else:
                for production in self.grammar.terminals: 
                    if production.match(self.tokens):
                        chunk = self.consume(len(production.body)) 
                        yield production.build(chunk) 
                        break 
                else: 
                    token = self.consume(1).pop()
                    yield Node('Text', value=token.value)
             
def link_builder(tokens: Sequence[Token]) -> Node:
    return Node("Link", metadata={"label": tokens[1].value, "target": tokens[4].value})

def image_builder(tokens: Sequence[Token]) -> Node:
    return Node("Image", metadata={"alt": tokens[2].value, "src": tokens[5].value})

grammar = Grammar([
    Production("Bold", ["STAR","STAR","CONTENT","STAR","STAR"]),
    Production("Italic", ["STAR","CONTENT","STAR"]),
    Production("InlineMath", ["SIGN","CONTENT","SIGN"]),
    Production("BlockMath", ["SIGN","SIGN","CONTENT","SIGN","SIGN"]),
    Production("CodeInline", ["BACKTICK","CONTENT","BACKTICK"]),
    Production("CodeBlock", ["BACKTICK","BACKTICK","BACKTICK","CONTENT","BACKTICK","BACKTICK","BACKTICK"]),
    Production("Link", ["LBRACK","TEXT","RBRACK","LPAREN","TEXT","RPAREN"], builder=link_builder),
    Production("Image", ["BANG","LBRACK","TEXT","RBRACK","LPAREN","TEXT","RPAREN"], builder=image_builder),
])

parser = Parser(grammar)

# ----------------------------
# Examples
# ----------------------------

# **bold and *italic* emph**
tokens1 = [
    Token("STAR", "*"), Token("STAR", "*"),
    Token("TEXT", "bold and "),
    Token("STAR", "*"),
    Token("TEXT", "italic"),
    Token("STAR", "*"),
    Token("TEXT", " emph"),
    Token("STAR", "*"), Token("STAR", "*"),
]

# *italic and **bold** emph*
tokens2 = [
    Token("STAR", "*"),
    Token("TEXT", "italic and "),
    Token("STAR", "*"), Token("STAR", "*"),
    Token("TEXT", "bold"),
    Token("STAR", "*"), Token("STAR", "*"),
    Token("TEXT", " emph"),
    Token("STAR", "*"),
]

# $x + y$
tokens3 = [
    Token("SIGN", "$"),
    Token("TEXT", "x + y"),
    Token("SIGN", "$"),
]

# $$f(x) = x*y$$
tokens4 = [
    Token("SIGN", "$"), Token("SIGN", "$"),
    Token("TEXT", "f(x) = x*y"),
    Token("SIGN", "$"), Token("SIGN", "$"),
]

# `inline code`
tokens5 = [
    Token("BACKTICK", "`"),
    Token("TEXT", "inline code"),
    Token("BACKTICK", "`"),
]

# ```block code```
tokens6 = [
    Token("BACKTICK", "`"), Token("BACKTICK", "`"), Token("BACKTICK", "`"),
    Token("TEXT", "print('hi')"),
    Token("BACKTICK", "`"), Token("BACKTICK", "`"), Token("BACKTICK", "`"),
]

# [docs](https://example.com)
tokens7 = [
    Token("LBRACK", "["),
    Token("TEXT", "docs"),
    Token("RBRACK", "]"),
    Token("LPAREN", "("),
    Token("TEXT", "https://example.com"),
    Token("RPAREN", ")"),
]

# ![diagram](fig.png)
tokens8 = [
    Token("BANG", "!"),
    Token("LBRACK", "["),
    Token("TEXT", "diagram"),
    Token("RBRACK", "]"),
    Token("LPAREN", "("),
    Token("TEXT", "fig.png"),
    Token("RPAREN", ")"),
]

 
for idx, toks in enumerate([tokens1, tokens2, tokens3, tokens4, tokens5, tokens6, tokens7, tokens8], start=1):
    print(f"\n--- example {idx} ---")
    for tok in toks:
        parser.push(tok)
    print(Node('Document', children=list(parser.flush())))
