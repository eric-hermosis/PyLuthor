from __future__ import annotations
from re import compile
from typing import Generator, List, Sequence, Any, Deque
from collections import deque
from io import StringIO
from dataclasses import dataclass

# --- Lexical Engine ---

@dataclass
class Token:
    name: str
    value: str | None = None

class Lexicon:
    def __init__(self, rules: dict[str, str]):
        self.rules = [(name, compile(pattern)) for name, pattern in rules.items()]

class Scanner:
    def __init__(self, lexicon: Lexicon):
        self.lexicon = lexicon

    def scan(self, stream: StringIO) -> Generator[Token, None, None]:
        for line in stream:
            pos = 0
            while pos < len(line):
                for name, pattern in self.lexicon.rules:
                    match = pattern.match(line, pos)
                    if match:
                        yield Token(name, match.group(0))
                        pos = match.end()
                        break
                else:
                    yield Token("TEXT", line[pos])
                    pos += 1

# --- AST & Parser ---

class Node:
    def __init__(self, kind: str, value: Any = None):
        self.kind = kind
        self.value = value
        self.children: List[Node] = []
        self.metadata: dict = {}

    def link(self, node: Node):
        self.children.append(node)

    def __repr__(self, indent: int = 0) -> str:
        pad = "  " * indent
        val = f"({self.value!r})" if self.value is not None else ""
        meta = f" {self.metadata}" if self.metadata else ""
        head = f"{self.kind}{val}{meta}"
        if not self.children: return pad + head
        return pad + head + "\n" + "\n".join(c.__repr__(indent + 1) for c in self.children)

class Production:
    def __init__(self, head: str, tokens: List[str]):
        self.head = head
        self.tokens = tokens
        self.is_recursive = "BODY" in tokens
        self.parts = self._split_parts()

    def _split_parts(self):
        res = []
        curr = []
        for t in self.tokens:
            if t == "BODY":
                res.append(curr); curr = []
            else: res.append(t)
        if curr: res.append(curr)
        # For simplicity in this parser, we assume one BODY: [opener, closer]
        return [res[0], res[1]] if self.is_recursive else [self.tokens]

class Parser:
    def __init__(self, productions: List[Production]):
        self.recursions = [p for p in productions if p.is_recursive]
        self.terminals = [p for p in productions if not p.is_recursive]
        self.tokens: Deque[Token] = deque()

    def parse(self, stopper: List[str] = None) -> List[Node]:
        nodes = []
        while self.tokens:
            if stopper and len(self.tokens) >= len(stopper):
                if all(self.tokens[i].name == stopper[i] for i in range(len(stopper))):
                    for _ in range(len(stopper)): self.tokens.popleft()
                    return nodes

            # Try Recursions (Bold, Link, etc.)
            found = False
            for p in self.recursions:
                opener = p.parts[0]
                if len(self.tokens) >= len(opener) and all(self.tokens[i].name == opener[i] for i in range(len(opener))):
                    node = Node(p.head)
                    for _ in range(len(opener)): self.tokens.popleft()
                    node.children = self.parse(stopper=p.parts[1])
                    nodes.append(node)
                    found = True; break
            if found: continue

            # Try Terminals
            for p in self.terminals:
                body = p.parts[0]
                if len(self.tokens) >= len(body) and all(self.tokens[i].name == body[i] for i in range(len(body))):
                    node = Node(p.head)
                    for _ in range(len(body)):
                        t = self.tokens.popleft()
                        node.link(Node(t.name, t.value))
                    nodes.append(node)
                    found = True; break
            if found: continue

            t = self.tokens.popleft()
            nodes.append(Node("TEXT", t.value))
        return nodes

# --- Block Aggregator ---

class Aggregator:
    def aggregate(self, nodes: List[Node]) -> Node:
        # 1. Group into lines
        lines: List[List[Node]] = []
        curr_line = []
        for n in nodes:
            if n.kind == "<|BREAK|>":
                lines.append(curr_line); curr_line = []
            else: curr_line.append(n)
        if curr_line: lines.append(curr_line)

        root = Node("Root")
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line: 
                i += 1; continue

            # Detect Header
            if line[0].kind == "<|HEADER|>":
                h = Node("Header", value=line[0].value)
                h.children = line[1:]
                root.link(h)
                i += 1
            # Detect Table
            elif any(n.kind == "<|BAR|>" for n in line):
                table = Node("Table")
                while i < len(lines) and any(n.kind == "<|BAR|>" for n in lines[i]):
                    table.link(self._build_row(lines[i]))
                    i += 1
                i = self._attach_caption(table, lines, i, "table:")
                root.link(table)
            # Default: Paragraph / Normal Nodes
            else:
                for n in line: root.link(n)
                i += 1
        return root

    def _build_row(self, line: List[Node]) -> Node:
        row = Node("TableRow")
        cell = Node("TableCell")
        for n in line:
            if n.kind == "<|BAR|>":
                if cell.children: row.link(cell)
                cell = Node("TableCell")
            else: cell.link(n)
        if cell.children: row.link(cell)
        return row

    def _attach_caption(self, parent: Node, lines: List[List[Node]], start: int, prefix: str) -> int:
        idx = start
        if idx < len(lines) and lines[idx] and lines[idx][0].kind == "Link":
            link_node = lines[idx][0]
            # Link structure: [0]:[, [1...]:Label, [next]:], [next]:(, [last-1]:Target, [last]:)
            # We look for the target in the metadata or children
            target_str = "".join(str(c.value) for c in link_node.children if c.value)
            if prefix in target_str:
                parent.metadata["caption"] = lines[idx]
                parent.metadata["id"] = target_str.split(prefix)[-1].strip(")")
                return idx + 1
        return idx

# --- Implementation ---

lex = Lexicon({
    "<|HEADER|>": r"^#{1,3}",
    "<|SIGN|>": r"\$\$|\$",
    "<|STAR|>": r"\*\*|\*",
    "<|BRAKET|>": r"\[|\]",
    "<|PAREN|>": r"\(|\)",
    "<|BAR|>": r"\|",
    "<|BREAK|>": r"\n",
    "SPACE": r"\s+",
})

# Define productions using token names
prods = [
    Production("Bold", ["<|STAR|>", "BODY", "<|STAR|>"]),
    Production("Math", ["<|SIGN|>", "BODY", "<|SIGN|>"]),
    Production("Link", ["<|BRAKET|>", "BODY", "<|BRAKET|>", "<|PAREN|>", "BODY", "<|PAREN|>"]),
]

if __name__ == "__main__":
    example = """# Title
| Col 1 | Col 2 |
| --- | --- |
| $x=1$ | **Bold** |
[Table 1:](table:test) My caption."""

    scanner = Scanner(lex)
    parser = Parser(prods)
    for t in scanner.scan(StringIO(example)):
        parser.tokens.append(t)
    
    ast_flat = parser.parse()
    final_tree = Aggregator().aggregate(ast_flat)
    print(final_tree)