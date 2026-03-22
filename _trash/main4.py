from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Callable, Dict
 
@dataclass(frozen=True)
class Token:
    name: str
    value: str

@dataclass(frozen=True)
class Production:
    head: str
    body: list[str]
    builder: Optional[Callable[[list[Token]], Node]] = None  # optional semantic action

    @property
    def is_recursive(self) -> bool:
        return "CONTENT" in self.body

    @property
    def opener(self) -> list[str]:
        if "CONTENT" not in self.body:
            return self.body
        index = self.body.index("CONTENT")
        return self.body[:index]

    @property
    def closer(self) -> list[str]:
        if "CONTENT" not in self.body:
            return []
        index = self.body.index("CONTENT")
        return self.body[index + 1:]
 
@dataclass
class Grammar:
    productions: list[Production]

    @property
    def recursive(self) -> list[Production]:
        return sorted(
            [production for production in self.productions if production.is_recursive],
            key=lambda production: len(production.opener),
            reverse=True
        )

    @property
    def flat(self) -> list[Production]:
        return sorted(
            [production for production in self.productions if not production.is_recursive],
            key=lambda production: len(production.body),
            reverse=True
        )

# ----------------------------
# AST
# ----------------------------
@dataclass
class Node:
    kind: str
    value: Optional[str] = None
    attrs: Dict[str, str]  | None = None
    children: list['Node'] | None = None

    def __post_init__(self):
        if self.attrs is None:
            self.attrs = {}
        if self.children is None:
            self.children = []

    def __repr__(self, level: int = 0) -> str:
        pad = "  " * level
        extra = []
        if self.value is not None:
            extra.append(repr(self.value))
        if self.attrs:
            extra.append(repr(self.attrs))
        head = self.kind if not extra else f"{self.kind}(" + ", ".join(extra) + ")"
        if not self.children:
            return pad + head
        out = [pad + head]
        for child in self.children:
            out.append(child.__repr__(level + 1))
        return "\n".join(out)

# ----------------------------
# Parser
# ----------------------------
class Parser:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.recursive = grammar.recursive
        self.flat = grammar.flat

    def parse(self, tokens: list[Token]) -> Node:
        self.tokens = tokens
        self.i = 0
        return Node("Document", children=self._parse_until(stop=None))

    def _run_len(self) -> int:
        if self.i >= len(self.tokens):
            return 0
        name = self.tokens[self.i].name
        j = self.i
        while j < len(self.tokens) and self.tokens[j].name == name:
            j += 1
        return j - self.i

    def _starts_with(self, seq: list[str]) -> bool:
        if self.i + len(seq) > len(self.tokens):
            return False
        return all(self.tokens[self.i + k].name == seq[k] for k in range(len(seq)))

    def _consume(self, n: int) -> list[Token]:
        out = self.tokens[self.i:self.i+n]
        self.i += n
        return out

    def _parse_until(self, stop: tuple[str,int]|None) -> list[Node]:
        nodes: list[Node] = []
        while self.i < len(self.tokens):
            run = self._run_len()
            name = self.tokens[self.i].name
 
            if stop is not None and (name, run) == stop:
                self.i += run
                return nodes
 
            opened = False
            for prod in self.recursive:
                opener = prod.opener
                closer = prod.closer
                if len(set(opener)) == 1 and run >= len(opener) and name == opener[0]:
                    self.i += len(opener)
                    inner = self._parse_until(stop=(opener[0], len(closer)))
                    nodes.append(Node(prod.head, children=inner))
                    opened = True
                    break
            if opened:
                continue
 
            matched = False
            for prod in self.flat:
                if self._starts_with(prod.body):
                    chunk = self._consume(len(prod.body))
                    if prod.builder:
                        nodes.append(prod.builder(chunk))
                    else:
                        nodes.append(Node(prod.head, value="".join(t.value for t in chunk if t.name=="TEXT")))
                    matched = True
                    break
            if matched:
                continue
 
            tok = self.tokens[self.i]
            nodes.append(Node("Text", value=tok.value))
            self.i += 1

        return nodes 

def link_builder(tokens: list[Token]) -> Node:
    return Node("Link", attrs={"label": tokens[1].value, "target": tokens[4].value})

def image_builder(tokens: list[Token]) -> Node:
    return Node("Image", attrs={"alt": tokens[2].value, "src": tokens[5].value})

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
    print(parser.parse(toks))