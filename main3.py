from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from re import Match, Pattern, compile
from typing import Any, Callable, Deque, Generator, Iterable, Sequence
from collections import deque
 
class Symbol:
    name: str
    form: str
    
    def __init__(self, name: str, form: str) -> None:
        self.name = name
        self.form = form

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Symbol):
            return self.name == value.name and self.form == value.form
        else:
            return False


class Rule:
    symbol: Symbol
    pattern: Pattern[str]
    category: str | None

    def __init__(self, symbol: Symbol, pattern: str, category: str | None = None) -> None:
        self.symbol = symbol
        self.pattern = compile(pattern)
        self.category = category

    def match(self, chunk: str, position: int = 0) -> Match[str] | None:
        return self.pattern.match(chunk, position)

    @property
    def terminal(self) -> str:
        return self.symbol.form
    

class Token:
    name : str
    value: str | None

    def __init__(self, name: str, value: str | None = None):
        self.name  = name
        self.value = value

    def __repr__(self):
        return f"Token({self.name}, {self.value!r})" if self.value else f"Token({self.name})"
 

class Lexicon:
    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = list(rules) 


class Scanner:  
    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon
        self.state: tuple[str, str] | None = None
        self.buffer: list[str] = []

    def flush(self) -> Generator[Token, None, None]:
        if not self.buffer:
            return

        lemma = self.state[0] if self.state else "TEXT"
        value = "".join(self.buffer)
        self.buffer.clear()

        if lemma == "TEXT" and value.strip() == "":
            return

        yield Token(lemma, value)

    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        position = 0

        while position < len(chunk):
            for rule in self.lexicon.rules:
                if self.state and self.state != (rule.category, rule.terminal):
                    continue

                match = rule.match(chunk, position)
                if not match:
                    continue

                yield from self.flush()

                groups = match.groups()
                for group in groups:
                    if group is None:
                        continue

                    if group == rule.terminal:
                        yield Token(rule.symbol.name, group)

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
                position += 1

        if not self.state:
            yield from self.flush()

    def scan(self, stream: Iterable[str]) -> Generator[Token, None, None]:
        for line in stream:
            yield from self.analyze(line)


@dataclass
class Node:
    kind: str
    value: str | None = None
    metadata: dict[str, Any] | None = None
    children: list[Node] | None = None

    def __repr__(self, level: int = 0) -> str:
        pad = "  " * level
        head = self.kind

        extra: list[str] = []
        if self.value is not None:
            extra.append(repr(self.value))
        if self.metadata:
            extra.append(repr(self.metadata))
        if extra:
            head = f"{self.kind}({', '.join(extra)})"

        if not self.children:
            return pad + head

        parts = [pad + head]
        for child in self.children:
            parts.append(child.__repr__(level + 1))
        return "\n".join(parts)

    def link(self, node: Node) -> None:
        if self.children is None:
            self.children = []
        self.children.append(node)
        

Builder = Callable[[Sequence[Any]], Node]
 
class Production: 
    def __init__(self, head: str, body: Sequence[str], builder: Builder | None = None) -> None:
        self.head = head
        self.body = list(body)
        self.builder = builder

    @property
    def recursive(self) -> bool:
        return "CONTENT" in self.body

    @property
    def opener(self) -> tuple[str, ...]:
        if not self.recursive:
            return tuple(self.body)
        index = self.body.index("CONTENT")
        return tuple(self.body[:index])

    @property
    def closer(self) -> tuple[str, ...]:
        if not self.recursive:
            return tuple()
        index = self.body.index("CONTENT")
        return tuple(self.body[index + 1 :])

    def matches(self, tokens: Sequence[Token]) -> bool:
        if len(tokens) < len(self.body):
            return False
        return all(tokens[i].name == self.body[i] for i in range(len(self.body)))

    def opens(self, tokens: Sequence[Token]) -> bool:
        if not self.recursive:
            return False
        if len(tokens) < len(self.opener):
            return False
        return all(tokens[i].name == self.opener[i] for i in range(len(self.opener)))

    def build_terminal(self, tokens: Sequence[Token]) -> Node:
        if self.builder is not None:
            return self.builder(tokens)
        return Node(self.head)

    def build_recursive(self, children: Sequence[Node]) -> Node:
        if self.builder is not None:
            return self.builder(children)
        return Node(self.head, children=list(children)) 
    

@dataclass
class Grammar:
    productions: list[Production]
    content: dict[str, str]

    @property
    def recursions(self) -> list[Production]:
        return sorted(
            [production for production in self.productions if production.recursive],
            key=lambda production: len(production.opener),
            reverse=True,
        )

    @property
    def terminals(self) -> list[Production]:
        return sorted(
            [production for production in self.productions if not production.recursive],
            key=lambda p: len(p.body),
            reverse=True,
        )
    

class Parser:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self.tokens: Deque[Token] = deque()

    def push(self, token: Token) -> None:
        self.tokens.append(token) 

    def matches(self, signature: Sequence[str]) -> bool: 
        if len(self.tokens) < len(signature):
            return False
        other = tuple(token.name for token in list(self.tokens)[:len(signature)])
        return other == tuple(signature)

    def consume(self, amount: int) -> list[Token]:
        return [self.tokens.popleft() for _ in range(amount)]

    def flush(self) -> Generator[Node, None, None]:
        yield from self.parse()

    def parse(self, closing: tuple[str, ...] | None = None) -> Generator[Node, None, None]:
        while self.tokens:
            if closing and self.matches(closing):
                self.consume(len(closing))
                break

            for production in self.grammar.recursions:
                if production.opens(list(self.tokens)):
                    self.consume(len(production.opener))
                    children = list(self.parse(closing=production.closer))
                    yield production.build_recursive(children)
                    break
            else:
                for production in self.grammar.terminals:
                    if production.matches(list(self.tokens)):
                        chunk = self.consume(len(production.body))
                        yield production.build_terminal(chunk)
                        break
                else:
                    token = self.consume(1)[0]
                    type = self.grammar.content.get(token.name, "Text")
                    yield Node(type, value=token.value)

def wrap(kind: str, **metadata: Any) -> Builder:
    def builder(children: Sequence[Any]) -> Node:
        return Node(kind, metadata=metadata or None, children=list(children)) 
    return builder 

def heading(kind: str, level: int) -> Builder:
    return wrap(kind, level=level)
 
def link_builder(tokens: Sequence[Any]) -> Node: 
    label  = tokens[1].value if len(tokens) > 1 else None
    target = tokens[3].value if len(tokens) > 3 else None
    return Node("Link", metadata={"label": label or "", "target": target or ""})
 
def figure_builder(tokens: Sequence[Any]) -> Node: 
    alt = tokens[1].value if len(tokens) > 1 else None
    src = tokens[3].value if len(tokens) > 3 else None
    return Node("Figure", metadata={"alt": alt or "", "src": src or ""})
  
class Markdown:
    lexicon = Lexicon(
        [
            Rule(Symbol("ENDL", "\n"), r"(\n)"),
            Rule(Symbol("H4", "####"), r"(^####)(?:\s*)(.*?)(\n|$)"),
            Rule(Symbol("H3", "###"), r"(^###)(?:\s*)(.*?)(\n|$)"),
            Rule(Symbol("H2", "##"), r"(^##)(?:\s+)(.*?)(\n|$)"),
            Rule(Symbol("H1", "#"), r"(^#)(?:\s+)(.*?)(\n|$)"),
            Rule(Symbol("LINK", "["), r"(\[)(.*?)(\]\()(.*?)(\))"),
            Rule(Symbol("ITEM", "-"), r"(^[-\*])(?:\s+)(.*?)(\n|$)"),
            Rule(Symbol("ROW_START", "|"), r"(^\|)"),
            Rule(Symbol("ROW_END", "|"), r"(\|)(?=\s*\n|$)"),
            Rule(Symbol("PIPE", "|"), r"(\|)"),
            Rule(Symbol("FIG_OPEN", "!["), r"(\!\[)"),
            Rule(Symbol("FIG_SEP", "]("), r"(\]\()"),
            Rule(Symbol("CLOSE_PAREN", ")"), r"(\))"),
            Rule(Symbol("STAR2", "**"), r"(\*\*)(.*?)(\*\*)(?!\*)"),
            Rule(Symbol("STAR1", "*"), r"(\*)(.*?)(\*)"),
            Rule(Symbol("SIGN2", "$$"), r"(\$\$)", "MATH"),
            Rule(Symbol("SIGN1", "$"), r"(\$)(.*?)(\$)", "MATH"),
            Rule(Symbol("TICK3", "```"), r"(```)", "CODE"),
            Rule(Symbol("TICK1", "`"), r"(`)", "CODE"),
        ]
    )

    grammar = Grammar(
        productions=[
            Production("Title",         ["H1", "CONTENT", "ENDL"],    builder=heading("Title", 1)),
            Production("Section",       ["H2", "CONTENT", "ENDL"],    builder=heading("Section", 2)),
            Production("Subsection",    ["H3", "CONTENT", "ENDL"],    builder=heading("Subsection", 3)),
            Production("Subsubsection", ["H4", "CONTENT", "ENDL"], builder=heading("Subsubsection", 4)),
            Production("Item",   ["ITEM", "CONTENT", "ENDL"],      builder=wrap("Item")),
            Production("Bold",   ["STAR2", "CONTENT", "STAR2"],    builder=wrap("Bold")),
            Production("Italic", ["STAR1", "CONTENT", "STAR1"],    builder=wrap("Italic")),
            Production("Math[Block]",  ["SIGN2", "CONTENT", "SIGN2"], builder=wrap("Math[Block]")),
            Production("Math[Inline]", ["SIGN1", "CONTENT", "SIGN1"], builder=wrap("Math[Inline]")),
            Production("Code[Block]",  ["TICK3", "CONTENT", "TICK3"], builder=wrap("Code[Block]")),
            Production("Code[Inline]", ["TICK1", "CONTENT", "TICK1"], builder=wrap("Code[Inline]")),
            Production("Link",   ["LINK", "TEXT", "FIG_SEP", "TEXT", "CLOSE_PAREN"],     builder=link_builder),
            Production("Figure", ["FIG_OPEN", "TEXT", "FIG_SEP", "TEXT", "CLOSE_PAREN"], builder=figure_builder),
        ],
        content={
            "TEXT": "Text",
            "CODE": "CodeText",
            "MATH": "MathText",
            "ENDL": "Break",
            "FIG_SEP": "UrlSeparator",
            "CLOSE_PAREN": "Text",
            "PIPE": "ColumnSeparator",
            "ROW_START": "RowStart",
            "ROW_END": "RowEnd",
        },
    ) 
  

class Aggregator:
    def aggregate(self, nodes: Sequence[Node]) -> list[Node]:
        result: list[Node] = []
        i = 0

        while i < len(nodes):
            node = nodes[i]
 
            if node.kind == "Item":
                grouped, i = self._consume_list(nodes, i)
                result.append(grouped)
                continue
 
            if node.kind == "RowStart":
                grouped, i = self._consume_table(nodes, i) 
                grouped = self._attach_caption(grouped, nodes, i, "table:")
                result.append(grouped)
                continue
 
            if node.kind == "Figure":
                node, i = self._attach_caption(node, nodes, i + 1, "figure:")
                result.append(node)
                continue

            result.append(node)
            i += 1

        return result

    def _consume_list(self, nodes: Sequence[Node], start: int) -> tuple[Node, int]:
        items: list[Node] = [nodes[start]]
        i = start + 1

        while i < len(nodes):
            j = i
            while j < len(nodes) and nodes[j].kind == "Break":
                j += 1
            if j < len(nodes) and nodes[j].kind == "Item":
                items.append(nodes[j])
                i = j + 1
                continue
            break

        return Node("List", children=items), i

    def _consume_table(self, nodes: Sequence[Node], start: int) -> tuple[Node, int]:
        rows: list[Node] = []
        i = start

        while i < len(nodes) and nodes[i].kind == "RowStart":
            row_children: list[Node] = [nodes[i]]
            i += 1

            while i < len(nodes):
                row_children.append(nodes[i])
                if nodes[i].kind == "RowEnd":
                    i += 1
                    break
                i += 1

            rows.append(Node("TableRow", children=row_children))
            j = i
            while j < len(nodes) and nodes[j].kind == "Break":
                j += 1
            if j < len(nodes) and nodes[j].kind == "RowStart":
                i = j
                continue
            break

        return Node("Table", children=rows), i

    def _attach_caption(self, node: Node, nodes: Sequence[Node], start: int, target_prefix: str) -> Node | tuple[Node, int]:
        """
        If the next node is a Link with target starting with target_prefix,
        attach it as a caption (include following inline nodes until Break).
        """
        if start >= len(nodes):
            return node if node.kind != "Figure" else (node, start)

        caption_nodes: list[Node] = []
        i = start

        # skip leading Breaks
        while i < len(nodes) and nodes[i].kind == "Break":
            i += 1

        # check for caption Link
        if i < len(nodes):
            first = nodes[i]
            if first.kind == "Link" and first.metadata.get("target", "").startswith(target_prefix):
                caption_nodes.append(first)
                i += 1
                # grab all inline nodes until next Break
                while i < len(nodes) and nodes[i].kind != "Break":
                    caption_nodes.append(nodes[i])
                    i += 1

                if node.metadata is None:
                    node.metadata = {}
                node.metadata["caption"] = caption_nodes
                node.metadata["id"] = first.metadata.get("target", "")

        return node if node.kind != "Figure" else (node, i) 

class Include:
    def __init__(self, filename: str) -> None:
        self.path = self.find(filename)
        self.scanner = Scanner(Markdown.lexicon)
        self.parser  = Parser (Markdown.grammar)
        self.aggregator = Aggregator()

    @staticmethod
    def find(filename: str) -> Path:
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".md")
        if not path.exists():
            raise FileNotFoundError(f"ERROR: File {path} not found.")
        return path

    def parse(self) -> Generator[Node, None, None]:
        with self.path.open(encoding="utf-8") as file:
            for token in self.scanner.scan(file):
                self.parser.push(token)
            yield from self.parser.flush() 

    def aggregate(self) -> Node:
        children = list(self.parse())
        return Node("Root", children=self.aggregator.aggregate(children)) 

if __name__ == "__main__":
    include = Include("example")
    root = include.aggregate()
    print(root)