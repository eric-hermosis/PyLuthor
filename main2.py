from __future__ import annotations
from typing import Iterator, Generator
from typing import Sequence  
from typing import List
from re import Pattern, Match 
from re import compile

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
    symbol  : Symbol
    pattern : Pattern[str] 
    category: str | None

    def __init__(self, symbol: Symbol, pattern: str, category: str | None = None) -> None:
        self.symbol   = symbol
        self.pattern  = compile(pattern) 
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
    rules: List[Rule]

    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = list(rules)

class Scanner:
    def __init__(self, lexicon: Lexicon):
        self.lexicon = lexicon 
        self.state   = None
        self.buffer  = [] 

    def flush(self) -> Generator[Token, None, None]:
        if self.buffer: 
            lemma = self.state[0] if self.state else 'TEXT'
            value = ''.join(self.buffer)
            self.buffer.clear()  
            if lemma == 'TEXT' and value.strip() == '':
                return  
            yield Token(lemma, value)

    def analyze(self, chunk: str) -> Generator[Token, None, None]:
        position = 0

        while position < len(chunk):      
            for rule in self.lexicon.rules: 
                if self.state and self.state != (rule.category, rule.terminal):
                    continue

                match = rule.match(chunk, position)
                if match:
                    yield from self.flush()   

                    for group in match.groups():     
                        
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
                position+=1 

        if not self.state:
            yield from self.flush()

    def scan(self, stream: Iterator[str]) -> Generator[Token, None, None]:
        for line in stream: 
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
        self.tokens  = []

    def push(self, token: Token):
        self.tokens.append(token)

    def flush(self) -> Generator[Node, None, None]:
        root = self.parse(self.tokens)
        yield from root.children          

    def parse(self, tokens: Sequence[Token]) -> Node:
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
    

class Markdown:

    lexicon = Lexicon([
        Rule(Symbol('ENDL', '\n'), r'(\n)'), 
        Rule(Symbol('H4', '####'), r'(^####)(?:\s*)(.*?)(\n|$)'),
        Rule(Symbol('H3', '###'), r'(^###)(?:\s*)(.*?)(\n|$)'),
        Rule(Symbol('H2', '##'), r'(^##)(?:\s)(.*?)(\n|$)'),
        Rule(Symbol('H1', '#'), r'(^#)(?:\s)(.*?)(\n|$)'), 
        Rule(Symbol('LINK', '['), r'(\[)(.*?)(\]\()(.*?)(\))'), 
        Rule(Symbol('ITEM', '-'), r'(^[-\*])(?:\s+)(.*?)(\n|$)'), 
        Rule(Symbol('ROW_START', '|'), r'(^\|)'),
        Rule(Symbol('ROW_END', '|'), r'(\|)(?=\s*\n|$)'),
        Rule(Symbol('PIPE', '|'), r'(\|)'), 
        Rule(Symbol('FIG_OPEN', '!['), r'(\!\[)'),
        Rule(Symbol('FIG_SEP', ']('), r'(\]\()'),
        Rule(Symbol('CLOSE_PAREN', ')'), r'(\))'), 
        Rule(Symbol('STAR', '**'), r'(\*\*)(.*?)(\*\*)(?!\*)'),
        Rule(Symbol('STAR', '*'), r'(\*)(.*?)(\*)'), 
        Rule(Symbol('SIGN', '$$'), r'(\$\$)', 'MATH'),
        Rule(Symbol('SIGN', '$'), r'(\$)(.*?)(\$)', 'MATH'), 
        Rule(Symbol('TICK', '```'), r'(\```)', 'CODE'),
        Rule(Symbol('TICK', '`'), r'(\`)', 'CODE'),
    ])

    grammar = Grammar( 
        productions=[   
            Production('Title',        ['H1', '#',   'ENDL', '\n']),
            Production('Link',         ['LINK', '[', 'CLOSE_PAREN', ')']),
            Production('Section',      ['H2', '##',  'ENDL', '\n']),
            Production('Subsection',   ['H3', '###', 'ENDL', '\n']), 
            Production('Item',         ['ITEM', '-', 'ENDL', '\n']),
            Production('TableRow',     ['ROW_START', '|', 'ROW_END', '|']),
            Production('Figure',       ['FIG_OPEN', '![', 'CLOSE_PAREN', ')']),
                        
            Production('Bold',         ['STAR', '**']), 
            Production('Italic',       ['STAR', '*']),  
            Production('Math[Block]',  ['SIGN', '$$']), 
            Production('Math[Inline]', ['SIGN', '$']),  
            Production('Code[Block]',  ['TICK', '```']),
            Production('Code[Inline]', ['TICK', '`']),  
        ],

        content={
            'TEXT': 'Text',
            'ITEM': 'Item',
            'MATH': 'Math[Content]',
            'CODE': 'Code[Content]',
            'ENDL': 'Break',
            'FIG_SEP': 'UrlSeparator',   
            'CLOSE_PAREN': 'Text',
            'PIPE': 'ColumnSeparator',
        }
    )
 
from pathlib import Path

class Include:
    node: Node

    @staticmethod
    def find(filename: str) -> Path:
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix('.md')
        if not path.exists():
            raise Exception(f"ERROR: File {path} not found.")
        return path

    def __init__(self, filename: str) -> None:
        self.path = self.find(filename) 
        self.scanner = Scanner(Markdown.lexicon)
        self.parser  = Parser (Markdown.grammar)

    def parse(self) -> Generator[Node, None, None]: 
        with self.path.open(encoding='utf-8') as file:
            for token in self.scanner.scan(file):
                self.parser.push(token)
            yield from self.parser.flush()

if __name__ == '__main__':
    include = Include('example')
    for node in include.parse():
        print(node)