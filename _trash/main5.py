from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Generator, Iterator, Sequence


# ----------------------------
# Tokens / lexing
# ----------------------------

@dataclass(slots=True)
class Token:
    name: str
    value: str | None = None

    def __repr__(self) -> str:
        return f"Token({self.name})" if self.value is None else f"Token({self.name}, {self.value!r})"


@dataclass(slots=True)
class Rule:
    name: str
    literal: str
    repeat: int = 1
    category: str | None = None  # "MATH" or "CODE" for stateful spans

    def match(self, chunk: str, position: int) -> bool:
        return chunk.startswith(self.literal, position)


class Lexicon:
    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = sorted(list(rules), key=lambda r: len(r.literal), reverse=True)


class Scanner:
    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon
        self.buffer: list[str] = []
        self.state: tuple[str, str, str, int] | None = None
        # state = (content_token_name, closer_literal, delimiter_token_name, repeat)

    def flush(self) -> Generator[Token, None, None]:
        if self.buffer:
            text = "".join(self.buffer)
            self.buffer.clear()
            if text:
                yield Token("TEXT", text)

    def _emit_delimiter(self, rule: Rule) -> Generator[Token, None, None]:
        for _ in range(rule.repeat):
            yield Token(rule.name, rule.literal)

    def _has_future_closer(self, chunk: str, position: int, literal: str) -> bool:
        return chunk.find(literal, position + len(literal)) != -1

    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        position = 0

        while position < len(chunk):
            # Inside math/code: everything becomes content until the closer is found.
            if self.state is not None:
                content_name, closer, delim_name, repeat = self.state
                close_at = chunk.find(closer, position)

                if close_at == -1:
                    if position < len(chunk):
                        yield Token(content_name, chunk[position:])
                    break

                if close_at > position:
                    yield Token(content_name, chunk[position:close_at])

                for _ in range(repeat):
                    yield Token(delim_name, closer)

                position = close_at + len(closer)
                self.state = None
                continue

            for rule in self.lexicon.rules:
                if not rule.match(chunk, position):
                    continue

                # Stateful delimiters only open if a matching closer exists later.
                if rule.category is not None and not self._has_future_closer(chunk, position, rule.literal):
                    self.buffer.append(rule.literal)
                    position += len(rule.literal)
                    break

                yield from self.flush()
                yield from self._emit_delimiter(rule)

                if rule.category is not None:
                    content_name = "MATH_TEXT" if rule.category == "MATH" else "CODE_TEXT"
                    self.state = (content_name, rule.literal, rule.name, rule.repeat)

                position += len(rule.literal)
                break
            else:
                self.buffer.append(chunk[position])
                position += 1

        if self.state is None:
            yield from self.flush()

    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        yield from self.analyze("".join(stream))
        if self.state is None:
            yield from self.flush()


# ----------------------------
# AST / parsing
# ----------------------------

@dataclass(slots=True)
class Node:
    kind: str
    value: str | None = None
    metadata: dict[str, str] | None = None
    children: list[Node] = field(default_factory=list)

    def __repr__(self, level: int = 0) -> str:
        pad = "  " * level

        extra: list[str] = []
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

    def link(self, node: Node) -> None:
        self.children.append(node)


class Production:
    def __init__(
        self,
        head: str,
        body: Sequence[str],
        builder: Callable[[Sequence[Token]], Node] | None = None,
    ) -> None:
        self.head = head
        self.body = list(body)
        self.build = builder or self._default_builder

    def _default_builder(self, chunk: Sequence[Token]) -> Node:
        text = "".join(token.value or "" for token in chunk if token.name == "TEXT")
        return Node(self.head, value=text if text else None)

    @property
    def is_recursive(self) -> bool:
        return "CONTENT" in self.body

    @property
    def opener(self) -> list[str]:
        if "CONTENT" not in self.body:
            return self.body
        i = self.body.index("CONTENT")
        return self.body[:i]

    @property
    def closer(self) -> list[str]:
        if "CONTENT" not in self.body:
            return []
        i = self.body.index("CONTENT")
        return self.body[i + 1:]

    def match(self, tokens: Sequence[Token]) -> bool:
        if len(tokens) < len(self.body):
            return False
        return all(tokens[i].name == self.body[i] for i in range(len(self.body)))

    def opens(self, tokens: Sequence[Token]) -> bool:
        if len(tokens) < len(self.opener):
            return False
        return all(tokens[i].name == self.opener[i] for i in range(len(self.opener)))


@dataclass(slots=True)
class Grammar:
    productions: list[Production]
    content_map: dict[str, str] = field(default_factory=dict)

    @property
    def recursions(self) -> list[Production]:
        return sorted(
            [p for p in self.productions if p.is_recursive],
            key=lambda p: len(p.opener),
            reverse=True,
        )

    @property
    def terminals(self) -> list[Production]:
        return sorted(
            [p for p in self.productions if not p.is_recursive],
            key=lambda p: len(p.body),
            reverse=True,
        )


class Parser:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self.tokens: deque[Token] = deque()

    def push(self, token: Token) -> None:
        self.tokens.append(token)

    def _run(self) -> list[Token]:
        if not self.tokens:
            return []
        name = self.tokens[0].name
        out: list[Token] = []
        i = 0
        while i < len(self.tokens) and self.tokens[i].name == name:
            out.append(self.tokens[i])
            i += 1
        return out

    def _consume(self, count: int) -> list[Token]:
        return [self.tokens.popleft() for _ in range(count)]

    def _parse_until(self, stop: tuple[str, int] | None = None) -> Generator[Node, None, None]:
        while self.tokens:
            repeated = self._run()
            terminal = repeated[0].name
            run_len = len(repeated)

            # Close current recursive span only when the current run exactly matches the stop delimiter.
            if stop and terminal == stop[0] and run_len == stop[1]:
                self._consume(stop[1])
                return

            # Recursive productions: prefer longer openers first.
            opened = False
            for production in self.grammar.recursions:
                if production.opens(repeated):
                    opener_len = len(production.opener)
                    closer_len = len(production.closer)

                    start = len(self.tokens)
                    self._consume(opener_len)

                    inner = list(self._parse_until((terminal, closer_len)))
                    if len(self.tokens) < closer_len:
                        # No closer found; backtrack and treat opener as text.
                        while len(self.tokens) < start:
                            self.tokens.appendleft(Token("TEXT", self.tokens.popleft().value if self.tokens else None))
                        self.tokens.clear()
                        return

                    yield Node(production.head, children=inner)

                    # The closer has already been consumed by the recursive call.
                    opened = True
                    break

            if opened:
                continue

            # Flat productions.
            for production in self.grammar.terminals:
                if production.match(self.tokens):
                    chunk = self._consume(len(production.body))
                    yield production.build(chunk)
                    break
            else:
                token = self._consume(1)[0]
                kind = self.grammar.content_map.get(token.name, "Text")
                yield Node(kind, value=token.value)

    def parse(self) -> Generator[Node, None, None]:
        yield from self._parse_until(None)

    def document(self) -> Node:
        return Node("Document", children=list(self.parse()))


# ----------------------------
# Builders
# ----------------------------

def link_builder(tokens: Sequence[Token]) -> Node:
    return Node(
        "Link",
        metadata={
            "label": tokens[1].value or "",
            "target": tokens[4].value or "",
        },
    )


def image_builder(tokens: Sequence[Token]) -> Node:
    return Node(
        "Image",
        metadata={
            "alt": tokens[2].value or "",
            "src": tokens[5].value or "",
        },
    )


# ----------------------------
# Grammar / lexicon
# ----------------------------

grammar = Grammar(
    productions=[
        Production("Bold", ["STAR", "STAR", "CONTENT", "STAR", "STAR"]),
        Production("Italic", ["STAR", "CONTENT", "STAR"]),
        Production("BlockMath", ["SIGN", "SIGN", "CONTENT", "SIGN", "SIGN"]),
        Production("InlineMath", ["SIGN", "CONTENT", "SIGN"]),
        Production("CodeBlock", ["BACKTICK", "BACKTICK", "BACKTICK", "CONTENT", "BACKTICK", "BACKTICK", "BACKTICK"]),
        Production("CodeInline", ["BACKTICK", "CONTENT", "BACKTICK"]),
        Production("Link", ["LBRACK", "TEXT", "RBRACK", "LPAREN", "TEXT", "RPAREN"], builder=link_builder),
        Production("Image", ["BANG", "LBRACK", "TEXT", "RBRACK", "LPAREN", "TEXT", "RPAREN"], builder=image_builder),
    ],
    content_map={
        "TEXT": "Text",
        "MATH_TEXT": "MathText",
        "CODE_TEXT": "CodeText",
    },
)

lexicon = Lexicon(
    [
        Rule("BACKTICK", "```", repeat=3, category="CODE"),
        Rule("SIGN", "$$", repeat=2, category="MATH"),
        Rule("STAR", "**", repeat=2),
        Rule("BACKTICK", "`", repeat=1, category="CODE"),
        Rule("SIGN", "$", repeat=1, category="MATH"),
        Rule("STAR", "*", repeat=1),
        Rule("BANG", "!"),
        Rule("LBRACK", "["),
        Rule("RBRACK", "]"),
        Rule("LPAREN", "("),
        Rule("RPAREN", ")"),
    ]
)


# ----------------------------
# File wrapper
# ----------------------------

class Include:
    @staticmethod
    def find(filename: str) -> Path:
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".md")
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path

    def __init__(self, filename: str) -> None:
        self.path = self.find(filename)
        self.scanner = Scanner(lexicon)
        self.parser = Parser(grammar)

    def parse(self) -> Node:
        with self.path.open(encoding="utf-8") as file:
            for token in self.scanner.scan(file):
                self.parser.push(token)
        return self.parser.document()


if __name__ == "__main__":
    include = Include("example")
    node = include.parse()
    print(node)