from __future__ import annotations
from typing import List
from typing import Sequence
from typing import Iterator
from luthor.scanner import Token

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
  
class Production:
    def __init__(self, head: str, body: Sequence[str]) -> None:
        self.head = head
        self.body = list(body)  
        self.opener = (self.body[0], self.body[1]) 
        self.closer = (self.body[2], self.body[3]) if len(self.body) >= 4 else self.opener

class Grammar:
    def __init__(self, productions: List[Production], content: dict[str, str]): 
        self.productions = productions 
        self.content = content

class Parser:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar 
        self.openers = {prod.opener: prod for prod in grammar.productions}

    def parse(self, tokens: Iterator[Token]) -> Node:
        root = Node('Document') 
        stack: list[tuple[Production | None, Node]] = [(None, root)]

        for token in tokens:
            sig = (token.name, token.value) 
             
            active_prods = [p for p, _ in stack if p is not None]
            active_closers = [p.closer for p in active_prods]
             
            if sig in active_closers: 
                while stack:
                    popped_prod, node = stack.pop()
                    if popped_prod and popped_prod.closer == sig: 
                        stack[-1][1].link(node)
                        break  
                    else: 
                        stack[-1][1].link(node) 
             
            elif sig in self.openers: 
                prod = self.openers[sig]
                stack.append((prod, Node(prod.head)))
              
            else:
                node_type = self.grammar.content.get(token.name, 'Text') 
                stack[-1][1].link(Node(node_type, token.value))
 
        while len(stack) > 1:
            _, node = stack.pop()
            stack[-1][1].link(node)
 
        return root   