from __future__ import annotations

from collections import deque
from pathlib import Path
from re import Match, Pattern, compile
from typing import Generator, Iterator, List, Sequence

class Symbol:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Symbol):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False
    
    def __hash__(self) -> int:
        return hash(self.name) 
    
class Terminal(Symbol):
    """
    Reworked Terminal: 
    - name: The category/type (e.g., 'BRACKET')
    - context: The specific value matched (e.g., '[')
    """
    def __init__(self, name: str, context: str | None = None) -> None:
        super().__init__(name)
        self.context = context

    def __repr__(self) -> str:
        if self.context:
            return f"Terminal({self.name}, context={self.context!r})"
        return f"Terminal({self.name})"
    
    def __str__(self) -> str:
        return f"{self.name}-{self.context}" if self.context else self.name

class Nonterminal(Symbol):
    pass

class Rule:
    terminal: Terminal
    pattern : Pattern[str]
    content : str | None

    def __init__(self, terminal: Terminal | str, pattern: str | Pattern[str], content: str | None = None) -> None:
        self.terminal = terminal if isinstance(terminal, Terminal) else Terminal(terminal)
        self.pattern = compile(pattern) if isinstance(pattern, str) else pattern
        self.content = content

    def match(self, chunk: str, position: int) -> Match[str] | None:
        return self.pattern.match(chunk, position) 

class Lexicon:
    rules: List[Rule]

    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = list(rules) 

class Token:
    name: str
    value: object

    def __init__(self, name: str, value: object) -> None:
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.name}, {self.value!r})" if self.value else f"Token({self.name})" 

class Scanner:
    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon
        self.cursor = 0
        self.buffer: list[str] = []
        self.state: str | None = None

    def flush(self) -> Generator[Token, None, None]:
        if self.buffer:
            yield Token(self.state or 'TEXT', ''.join(self.buffer))
            self.buffer.clear()

    def push(self, char: str) -> None:
        self.buffer.append(char)
        self.cursor += 1

    def handle(self, match: Match[str], rule: Rule) -> Generator[Token, None, None]:
        yield from self.flush()
        yield Token(str(rule.terminal), match.group())
        self.cursor = match.end()

    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        self.cursor = 0
        while self.cursor < len(chunk):
            for rule in self.lexicon.rules:
                match = rule.match(chunk, self.cursor)
                if match:
                    if self.state and self.state == rule.content:
                        yield from self.handle(match, rule)
                        self.state = None
                        break
                    elif self.state:
                        self.push(chunk[self.cursor])
                        break
                    else:
                        yield from self.handle(match, rule)
                        self.state = rule.content
                        break
            else:
                self.push(chunk[self.cursor])

    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        for line in stream:
            yield from self.analyze(line)
        yield from self.flush() 


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


class Grammar:
    recursions: List[Production]
    terminals:  List[Production]

    def __init__(self, productions: Sequence[Production]) -> None:

        self.recursions = sorted(
            [production for production in productions if production.recursive],
            key=lambda production: len(production.opener),
            reverse=True,
        )

        self.terminals = sorted(
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
    

class Boundary:
    sequence: List[Sequence]

    def __init__(self, sequence: Sequence[str]) -> None:
        self.sequence = list(sequence)

    def matches(self, tokens: Sequence[Token]) -> bool:
        if len(tokens) < len(self.sequence):
            return False
        return all(tokens[index].name == self.sequence[index] for index in range(len(self.sequence)))


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
                for production in self.grammar.terminals:
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
 





from typing import Protocol, runtime_checkable

@runtime_checkable
class Expression(Protocol):
    def forward(self) -> Generator[Node, None, None]:
        ...

@runtime_checkable
class Renderable(Protocol):
    def render(self) -> str:
        ...
 
from enum import Enum

class Layout(Enum): 
    BLOCK  = "\\{name}{options}{arguments}\n" 
    INLINE = "\\{name}{options}{arguments}" 
    ENVIRONMENT = "\\{name}{arguments}{options}\n"

    def build(self, name: str, options: str, arguments: str) -> str:
        return self.value.format(name=name, options=options, arguments=arguments)

class Command(Node, Expression, Renderable):

    def __init__(self, name: str, arguments: Sequence[str] | None = None, options: Sequence[str] | str | None = None) -> None:
        super().__init__(f'Command({name}{arguments}')
        self.name = name
        self.arguments = list(arguments) if arguments else []
         
        if isinstance(options, str):
            self.options = [options]
        else:
            self.options = list(options) if options else []             

    def forward(self) -> Generator[Command, None, None]:
        yield self

    def render(self) -> str:
        options = getattr(self, 'options', [])
        options_str = f"[{','.join(options)}]" if options else ""
        args_str = "".join(f"{{{arg}}}" for arg in getattr(self, 'arguments', [])) 
        
        if self.name == "begin":
            return f"\\begin{args_str}{options_str}\n" 

        elif self.name in ("ref", "textbf", "textit"):
            return f"\\{self.name}{options_str}{args_str}"
             
        return f"\\{self.name}{options_str}{args_str}\n"
    
            
class Document(Node, Expression):

    def __init__(self, preamble: Sequence[Node], body: Sequence[Node]) -> None:
        super().__init__('Document')
        self.attach(Node('Preamble'), preamble)
        self.attach(Node('Body'), body)

    def attach(self, node: Node, children: Sequence[Node]) -> None:
        node.children.extend(children)
        self.link(node)   
 
    def forward(self) -> Generator[Node, None, None]:  
        for node in self.children[0].children:
            if isinstance(node, Expression):
                yield from node.forward()
            else:
                yield node
                    
        yield Command("begin", ["document"])  
        for node in self.children[1].children:
            if isinstance(node, Expression):
                yield from node.forward()
            else:
                yield node  
        yield Command("end", ["document"])  
             

class Geometry(Node, Expression):
    def __init__(
        self,
        paper: str = "a4paper",
        top: str | None = None,
        bottom: str | None = None,
        left: str | None = None,
        right: str | None = None,
    ) -> None:
        super().__init__('Geometry')
        self.paper = paper
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right 

    def forward(self) -> Generator[Command, None, None]:
        options = []
        if self.paper: options.append(self.paper)
        if self.top: options.append(f"top={self.top}")
        if self.bottom: options.append(f"bottom={self.bottom}")
        if self.left: options.append(f"left={self.left}")
        if self.right: options.append(f"right={self.right}")  
        yield Command("geometry", [", ".join(options)]) 

class Figure(Node, Expression):
    path: str
    label: str | None
    caption: str | None

    def __init__(self, path: str) -> None:
        super().__init__("Figure")
        self.path = path 
        self.label = None
        self.caption = None
        self.cursor = 0  

    def __repr__(self, indent: int = 0) -> str:
        padding = "  " * indent
             
        parts = [f"path={self.path!r}"]
        if self.caption:
            parts.append(f"caption={self.caption.strip()!r}")
        if self.label:
            parts.append(f"label={self.label!r}")
                
        return padding + f"Figure({', '.join(parts)})"

    def forward(self) -> Generator[Command, None, None]:
        yield Command("begin", ["figure"], options="h")
        yield Command("centering")
        yield Command("includegraphics", [self.path], options="width=\\linewidth") 
        if self.caption:
            yield Command("caption", [self.caption.strip()])
            
        if self.label:
            yield Command("label", [self.label])
            
        yield Command("end", ["figure"])  
    
 
class Reference(Node, Expression):
    target: str

    def __init__(self, target: str) -> None:
        super().__init__("Reference")
        self.target = target

    def __repr__(self, indent: int = 0) -> str:
        padding = "  " * indent
        return padding + f"Reference({self.target!r})"

    def forward(self) -> Generator[Command, None, None]:
        yield Command("ref", [self.target])


class Analyzer:
    def __init__(self) -> None:
        self.queue = deque()

    @property
    def top(self) -> Node | None:
        return self.queue[-1] if self.queue else None

    def flush(self) -> Generator[Node, None, None]:
        while self.queue:
            yield self.queue.popleft() 

    def push(self, node: Node) -> None:  
        self.queue.append(node)

    def flat(self, node: Node) -> str:  
        if node.type == 'TEXT':
            return str(node.value) or ""
        elif node.type == 'Math': 
            sign = node.children[0].value
            content = node.children[1].value
            return f"{sign}{content}{sign}"
        elif node.value is not None:
            return str(node.value)
             
        return "".join(self.flat(child) for child in node.children)

    def analyze(self, node: Node) -> Generator[Node, None, None]:
        match node.type:   
            case 'Figure':
                if isinstance(self.top, Figure):
                    yield from self.flush()
                 
                path = str(node.children[1].value)
                assert path
                self.push(Figure(path))
            
            case 'Link':
                target = str(node.children[1].value)
                assert target
                
                if isinstance(self.top, Figure):   
                    self.top.cursor = 0
                    self.top.label = target
                else:  
                    if target.startswith(("figure:", "table:", "equation:")):
                        self.push(Reference(target))
                    else:
                        self.push(node)  
                    yield from self.flush()
                    
            case 'ENDL':
                if isinstance(self.top, Figure):
                    self.top.cursor += 1
                    
                    if self.top.cursor > 1: 
                        yield from self.flush()
                        yield node
                    elif self.top.caption: 
                        self.top.caption += " "
                else:
                    yield from self.flush()
                    yield node

            case 'Head':
                yield from self.flush() 
                hashes = str(node.value).strip() if node.value else "#" 
                content = "".join(self.flat(child) for child in node.children).strip()
                
                cmd_name = {
                    1: "section", 
                    2: "subsection", 
                    3: "subsubsection"
                }.get(len(hashes), "section")
                
                self.push(Command(cmd_name, [content]))
                yield from self.flush()
                
            case 'Bold':
                yield from self.flush()
                content = "".join(self.flat(child) for child in node.children).strip()
                self.push(Command("textbf", [content]))
                yield from self.flush()

            case 'Italic':
                yield from self.flush()
                content = "".join(self.flat(child) for child in node.children).strip()
                self.push(Command("textit", [content]))
                yield from self.flush()

            case _:
                if isinstance(self.top, Figure):
                    text = self.flat(node) 
                    if text.strip():
                        self.top.cursor = 0
                        
                    self.top.caption = (self.top.caption or "") + text
                else:
                    self.push(node)
                    yield from self.flush()
            
class Markdown: 
    lexicon = Lexicon(
        [
            Rule(Terminal("HASH"), pattern=r"^#{1,3}(?=\s)"),
            Rule(Terminal("ENDL"), pattern=r"\n"),
            Rule(Terminal("LBRA"), pattern=r"\["),
            Rule(Terminal("RBRA"), pattern=r"\]"),
            Rule(Terminal("LPAR"), pattern=r"\("),
            Rule(Terminal("RPAR"), pattern=r"\)"),
            Rule(Terminal("SIGN"), pattern=r"\$(?=\s)",  content="MATH"),
            Rule(Terminal("SIGN"), pattern=r"(?<=\s)\$", content="MATH"),
            Rule(Terminal("SIGN"), pattern=r"\$\$",      content="MATH"),
            Rule(Terminal('MARK'), pattern=r"!"),
            Rule(Terminal("STAR2"), pattern=r"\*\*"),    
            Rule(Terminal("STAR1"), pattern=r"\*(?!\*)")
        ]
    )

    grammar = Grammar(
        [      
            Production("Head",   ["HASH", "BODY", "ENDL"]),
            Production("Math",   ["SIGN", "MATH", "SIGN"]),
            Production("Link",   ["LBRA", "BODY", "RBRA", "LPAR", "BODY", "RPAR"]),
            Production("Figure", ["MARK", "BRA",  "BODY", "RBRA", "LPAR", "BODY", "RPAR"]),
            Production("Bold",   ["STAR2","BODY", "STAR2"]),
            Production("Italic", ["STAR1","BODY", "STAR1"]),
        ]
    )

class Include(Node, Expression):

    @staticmethod
    def find(filename: str) -> Path:
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".md")
        if not path.exists():
            raise Exception(f"ERROR: File {path} not found.")
        return path

    def __init__(self, filename: str) -> None:
        super().__init__('Include')
        self.path = self.find(filename)
        self.scanner = Scanner(Markdown.lexicon)
        self.parser = Parser(Markdown.grammar)
        self.analyzer = Analyzer()
        for node in self.parse(): 
            self.link(node)

    def parse(self) -> Generator[Node, None, None]:
        with self.path.open("r", encoding="utf-8") as file:
            for token in self.scanner.scan(file):
                self.parser.push(token)

        for node in self.parser.flush():
            yield from self.analyzer.analyze(node) 

    def forward(self) -> Generator[Node, None, None]:
        for child in self.children: 
            if isinstance(child, Expression): 
                yield from child.forward() 
            else: 
                yield child

from typing import Callable, Dict


def render_text(node: Node) -> str:
    return str(node.value) or ""

def render_math(node: Node) -> str:
    sign = node.children[0].value
    content = node.children[1].value
    return f"{sign}{content}{sign}"

def render_endl(node: Node) -> str:
    return "\n"


class Latex: 
    handlers: Dict[str, Callable[[Node], str]]

    def __init__(self) -> None: 
        self.handlers = {
            'TEXT':    render_text,
            'Math':    render_math,
            'ENDL':    render_endl,
        } 

    def render(self, document: Document) -> str: 
        output = []
        
        for node in document.forward():  
            if isinstance(node, Renderable):
                output.append(node.render())
                 
            else:
                handler = self.handlers.get(node.type, lambda n: n.value or "") 
                output.append(handler(node))
                 
        return "".join(output)
    

if __name__ == "__main__":

    document = Document(
        preamble=[
            Command("documentclass", ["article"], options="12pt"),
            Command("usepackage", ["babel"],      options="spanish,provide=*"),
            Command("usepackage", ["inputenc"],   options="utf8"),
            Command("usepackage", ["fontenc"],    options="T1"),
            Command("usepackage", ["lmodern"]),
            Command("usepackage", ["amsmath"]),
            Command("usepackage", ["amssymb"]),
            Command("usepackage", ["hyperref"]),
            Command("usepackage", ["cite"]),
            Command("usepackage", ["graphicx"]),
            Command("usepackage", ["caption"],    options="font=small,labelfont=bf,margin=0.5cm"),
            Command("usepackage", ["geometry"]),
            Command(
                paper="a4paper",
                top="3.5cm",
                bottom="3.5cm",
                left="3.5cm",
                right="3.5cm"
            ),
            Command("setlength", ["\\parindent", "0pt"]),
            Command("setlength", ["\\parskip", "1em"]),
            Command("title",     ["Markdown Example"]),
            Command("author",    ["Eric Hermosis"]),
            Command("date",      ["\\today"]),
        ],

        body=[
            Include('example'), 
        ]
    ) 

    latex = Latex()
    tex = latex.render(document)
    print(tex) 