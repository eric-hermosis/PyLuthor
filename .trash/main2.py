from __future__ import annotations
from re import Match, Pattern, compile 
from typing import Generator, Iterator, List, Sequence
from luthor.lexicon import Nonterminal
from luthor.lexicon import Lexicon
from luthor.scanner import Scanner 
from luthor.scanner import Token
 
class Production:
    head: Nonterminal
    body: List[Terminal | Nonterminal]

    def __init__(self, head: str | Nonterminal, body: Sequence[str | Terminal | Nonterminal]) -> None:
        self.head = head if isinstance(head, Nonterminal) else Nonterminal(head)
        self.body = []
        for item in body:
            if item == 'BODY':
                self.body.append(Nonterminal('BODY'))
            elif isinstance(item, (Terminal, Nonterminal)):
                self.body.append(item)
            elif isinstance(item, str): 
                self.body.append(Terminal(item))
            else:
                raise TypeError(f"Invalid symbol type in body: {type(item)}")

        self.indices = [index for index, symbol in enumerate(self.body) if symbol == 'BODY']
        self.parts = self.split()

    def split(self) -> list[tuple[str, ...]]:
        parts = []
        start = 0
        for position in self.indices:
            parts.append(tuple(self.body[start:position]))
            start = position + 1
        parts.append(tuple(self.body[start:]))
        return parts

    @property
    def recursive(self) -> bool:
        return bool(self.indices)

    @property
    def order(self) -> int:
        return len(self.indices)

    @property
    def opener(self) -> tuple[str, ...]:
        return self.parts[0]

    @property
    def closer(self) -> tuple[str, ...]:
        return self.parts[-1] if self.recursive else tuple()

    def opens(self, tokens: Sequence[Token]) -> bool:
        if not self.recursive or len(tokens) < len(self.opener):
            return False
        return all(tokens[index].name == self.opener[index] for index in range(len(self.opener)))

    def closes(self, tokens: Sequence[Token]) -> bool:
        if not self.recursive or len(tokens) < len(self.closer):
            return False
        return all(tokens[index].name == self.closer[index] for index in range(len(self.closer)))

    def matches(self, tokens: Sequence[Token]) -> bool:
        if self.recursive or len(tokens) < len(self.body):
            return False
        return all(tokens[index].name == self.body[index] for index in range(len(self.body))) 


class Boundary:
    sequence: List[str]

    def __init__(self, sequence: Sequence[str]) -> None:
        self.sequence = list(sequence)

    def matches(self, tokens: Sequence[Token]) -> bool:
        if len(tokens) < len(self.sequence):
            return False
        return all(tokens[index].name == self.sequence[index] for index in range(len(self.sequence)))


class Grammar : 
    recursions : List[Production]
    imperations: List[Production]

    def __init__(self, productions: Sequence[Production]) -> None:

        self.recursions = sorted(
            [production for production in productions if production.recursive],
            key=lambda production: len(production.opener),
            reverse=True,
        )

        self.imperations = sorted(
            [production for production in productions if not production.recursive],
            key=lambda production: len(production.body),
            reverse=True,
        ) 


class Node:
    type: str
    value: object | None 
    children: list[Node]

    def __init__(self, type: str, value: object | None = None) -> None:
        self.type = type
        self.value = value
        self.children = []

    def link(self, node: Node) -> None:
        self.children.append(node)

    def __repr__(self, indent: int = 0) -> str:
        padding = "  " * indent
        head = self.type if self.value is None else f"{self.type}({self.value!r})"
        if not self.children:
            return padding + head
        
        lines = [padding + head]
        for child in self.children:
            lines.append(child.__repr__(indent + 1))
        return "\n".join(lines) 
    

from collections import deque
 
class Parser:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self.tokens = deque()

    def push(self, token: Token) -> None:
        self.tokens.append(token) 

    def consume(self, amount: int) -> list[Token]:
        return [self.tokens.popleft() for _ in range(amount)]

    def flush(self) -> Generator[Node, None, None]:
        yield from self.parse(None)

    def parse(self, boundary: Boundary  | None) -> Generator[Node, None, None]:  
        while self.tokens:
            if boundary and boundary.matches(self.tokens):
                break

            for production in self.grammar.recursions:
                if production.opens(self.tokens):
                    yield self.recurse(production)
                    break
            else:
                for production in self.grammar.imperations:
                    if production.matches(self.tokens):
                        tokens = self.consume(len(production.body))
                        yield self.terminate(production, tokens)
                        break
                else:
                    token = self.consume(1)[0]
                    yield Node(token.name, token.value) 

    def recurse(self, production: Production) -> Node: 
            opener_tokens = self.consume(len(production.opener)) 
            node = Node(str(production.head), value=opener_tokens[0].value)

            for index in range(production.order):
                next = production.parts[index + 1]  
                node.children.extend(self.parse(Boundary(next) if next else None))
                if next:
                    self.consume(len(next))
            return node

    def terminate(self, production: Production, tokens: Sequence[Token]) -> Node: 
        node = Node(str(production.head))
        for token in tokens:
            node.link(Node(token.name, token.value))
        return node 
 


from luthor.lexicon import Lexicon, Rule, Terminal

class Markdown:
    lexicon = Lexicon([ 
        Rule(Terminal("<|HEADER|>", "#"),   pattern=r"^#(?=\s)"),
        Rule(Terminal("<|HEADER|>", "##"),  pattern=r"^##(?=\s)"),
        Rule(Terminal("<|HEADER|>", "###"), pattern=r"^###(?=\s)"),
            
        Rule(Terminal("<|HYPHEN|>", "-"),  pattern=r"^\s*-(?=\s)"),
            
        Rule(Terminal("<|FENCE|>", "```"), pattern=r"[`]{3}", content="<|CODE|>"),
        Rule(Terminal("<|FENCE|>", "`"),   pattern=r"`",      content="<|CODE|>"),
        
        Rule(Terminal("<|SIGN|>", "$$"), pattern=r"\$\$",     content="<|MATH|>"),
        Rule(Terminal("<|SIGN|>", "$"),  pattern=r"\$(?!\$)", content="<|MATH|>"),
            
        Rule(Terminal("<|STAR|>", "**"), pattern=r"\*\*"),    
        Rule(Terminal("<|STAR|>", "*"),  pattern=r"\*(?!\*)"),
            
        Rule(Terminal("<|MARK|>", "!"), pattern=r"!"),
        Rule(Terminal("<|BRAKET|>", "["), pattern=r"\["),
        Rule(Terminal("<|BRAKET|>", "]"), pattern=r"\]"),
        Rule(Terminal("<|PARENTHESIS|>", "("), pattern=r"\("), 
        Rule(Terminal("<|PARENTHESIS|>", ")"), pattern=r"\)"), 
            
        Rule(Terminal("<|BAR|>", "|"),    pattern=r"\|"),
        Rule(Terminal("<|LINE|>", "---"), pattern=r"[-]{3,}"),
        Rule(Terminal("<|COLON|>", ":"),  pattern=r":"),
        Rule(Terminal("<|BREAK|>", "\n"), pattern=r"\n"),
    ]) 

from io import StringIO 
 
grammar = Grammar([       
    Production("Head", [
        Terminal("<|HEADER|>"), 
        Nonterminal("Body"), 
        Terminal("<|BREAK|>", "\n")
    ]),
 
    Production("Math", [
        Terminal("<|SIGN|>"), 
        Terminal("<|MATH|>"), 
        Terminal("<|SIGN|>")
    ]),
 
    Production("Link", [
        Terminal("<|BRAKET|>", "["), 
        Nonterminal("Body"), 
        Terminal("<|BRAKET|>", "]"), 
        Terminal("<|PARENTHESIS|>", "("), 
        Nonterminal("Body"), 
        Terminal("<|PARENTHESIS|>", ")"), 
    ]),
     
    Production("Figure", [
        Terminal("<|MARK|>", "!"), 
        Terminal("<|BRAKET|>", "["), 
        Nonterminal("Body"), 
        Terminal("<|BRAKET|>", "]"), 
        Terminal("<|PARENTHESIS|>", "("), 
        Nonterminal("Body"), 
        Terminal("<|PARENTHESIS|>", ")")
    ]),
 
    Production("Bold", [
        Terminal("<|STAR|>", "**"), 
        Nonterminal("Body"), 
        Terminal("<|STAR|>", "**")
    ]),
    
    Production("Italic", [
        Terminal("<|STAR|>", "*"), 
        Nonterminal("Body"), 
        Terminal("<|STAR|>", "*")
    ]),
 
    Production("Separator", [
        Terminal("<|LINE|>", "---")
    ])
]) 

if __name__ == '__main__':   
    example = StringIO("""
# Section

This is an example with **bold** and *italic* emphasis.

## Subsection

Inline math like $f(x) = x^2$ and math blocks:

$$
f(x,y,z) = xy + yz + zx,
$$

where:
- $f$ is a **function**,
- and $x$, $y$, $z$ are variables.

### Subsubsection
 
Inline `code` and code blocks:

```
def square(x):
	return x**2
```

| Header 1   | Header 2   |
| --------   | ---------- |
| Cell $x=1$ | Cell **b** |
[Table 1:](table:example) This is the *caption* of the table where $x=1$ is math and **b** have emphasis.

Here table [1](table:example) is a table. An example of an image:

![PyLuthor logo](logo.png)
[Figure 1:](figure:logo) This is the *caption* of the image.

Can be referenced as figure [1](figure:logo) just like with tables.                                  
""")
    scanner = Scanner(Markdown.lexicon)
    for token in scanner.scan(example):
        print(token, ",") 