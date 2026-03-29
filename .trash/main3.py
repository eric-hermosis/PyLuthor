from __future__ import annotations

from collections import deque
from re import Match, Pattern, compile
from typing import Iterator, Sequence


# =========================
# Symbols
# =========================

class Symbol:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Symbol):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def __hash__(self) -> int:
        return hash(self.name)


class Terminal(Symbol):
    def __init__(self, name: str, context: str | None = None) -> None:
        super().__init__(name)
        self.context = context

    def __str__(self) -> str:
        return f"{self.name}-{self.context}" if self.context else self.name


class Nonterminal(Symbol):
    pass


# =========================
# Lexer
# =========================

class Rule:
    def __init__(self, terminal: str, pattern: str | Pattern[str], content: str | None = None) -> None:
        self.terminal = terminal
        self.pattern = compile(pattern) if isinstance(pattern, str) else pattern
        self.content = content

    def match(self, chunk: str, position: int) -> Match[str] | None:
        return self.pattern.match(chunk, position)


class Lexicon:
    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = list(rules)


class Token:
    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.name}, {self.value!r})"


class Scanner:
    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon
        self.cursor = 0
        self.buffer: list[str] = []

    def flush(self):
        if self.buffer:
            yield Token("TEXT", "".join(self.buffer))
            self.buffer.clear()

    def push(self, char: str):
        self.buffer.append(char)
        self.cursor += 1

    def handle(self, match: Match[str], rule: Rule):
        yield from self.flush()
        yield Token(rule.terminal, match.group())
        self.cursor = match.end()

    def analyze(self, chunk: str):
        self.cursor = 0
        while self.cursor < len(chunk):
            for rule in self.lexicon.rules:
                match = rule.match(chunk, self.cursor)
                if match:
                    yield from self.handle(match, rule)
                    break
            else:
                self.push(chunk[self.cursor])

    def scan(self, stream: Iterator[str]):
        for line in stream:
            yield from self.analyze(line)
        yield from self.flush()


# =========================
# AST
# =========================

class Node:
    def __init__(self, type: str, value: str | None = None) -> None:
        self.type = type
        self.value = value
        self.children: list[Node] = []

    def link(self, node: "Node"):
        self.children.append(node)

    def __repr__(self, indent=0):
        pad = "  " * indent
        head = f"{self.type}({self.value!r})" if self.value else self.type
        if not self.children:
            return pad + head
        return pad + head + "\n" + "\n".join(child.__repr__(indent + 1) for child in self.children)


# =========================
# Inline Parser (Math)
# =========================

class InlineParser:
    def __init__(self):
        self.tokens = deque()

    def push(self, token: Token):
        self.tokens.append(token)

    def parse(self):
        while self.tokens:
            tok = self.tokens.popleft()

            if tok.name == "SIGN":
                yield self.parse_math(tok)
            else:
                yield Node(tok.name, tok.value)

    def parse_math(self, opener: Token) -> Node:
        node = Node("Math", opener.value)

        while self.tokens:
            tok = self.tokens.popleft()
            if tok.name == "SIGN":
                break
            node.link(Node(tok.name, tok.value))

        return node


# =========================
# Block Parser (Rows)
# =========================

class Parser:
    def __init__(self):
        self.tokens = deque()

    def push(self, token: Token):
        self.tokens.append(token)

    def consume(self):
        return self.tokens.popleft()

    def match(self, name: str):
        return self.tokens and self.tokens[0].name == name

    def parse(self):
        while self.tokens:
            if self.match("PIPE"):
                yield self.parse_row()
            else:
                tok = self.consume()
                yield Node(tok.name, tok.value)

    def parse_row(self) -> Node:
        self.consume() 
        row = Node("Row", "|")

        cell_tokens = []

        while self.tokens:
            if self.match("PIPE"):
                self.consume()
                row.link(self.build_cell(cell_tokens))
                cell_tokens = []
                continue

            if self.match("ENDL"):
                self.consume()
                if cell_tokens:
                    row.link(self.build_cell(cell_tokens))
                break

            cell_tokens.append(self.consume())

        return row

    def build_cell(self, tokens: list[Token]) -> Node:
        cell = Node("Cell")

        inline = InlineParser()
        for t in tokens:
            inline.push(t)

        for node in inline.parse():
            cell.link(node)

        return cell

 

class Markdown:
    lexicon = Lexicon(
        [
            Rule("ENDL", r"\n"),
            Rule("PIPE", r"\|"),
            Rule("SIGN", r"\$"),
        ]
    )


if __name__ == "__main__":
    from io import StringIO

    example = StringIO("""
| Header 1   | Header 2   |
| --------   | ---------- |
| Cell $x=1$ | Cell **b** |
""")

    scanner = Scanner(Markdown.lexicon)
    parser = Parser()

    for token in scanner.scan(example):
        parser.push(token)

    for node in parser.parse():
        print(node)