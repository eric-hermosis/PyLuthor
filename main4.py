from __future__ import annotations

from typing import Iterator, Generator
from typing import Sequence 
from typing import List
from re import Pattern, Match 
from re import compile

class Rule:
    name: str
    pattern : Pattern[str]
    terminal: str
    category: str | None

    def __init__(self, name: str, pattern: str, terminal: str, category: str | None = None) -> None:
        self.name = name
        self.pattern  = compile(pattern)
        self.terminal = terminal
        self.category = category

    def match(self, chunk: str, position: int = 0) -> Match[str] | None: 
        return self.pattern.match(chunk, position)  
 
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
        self.state  = None
        self.buffer = [] 

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
                            yield Token(rule.name, group)  
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

class Analyzer: 

    def __init__(self, root: Node):
        self.root = root

    def analyze(self) -> Node:
        self._collapse_tables(self.root)
        return self.root

    def _collapse_tables(self, parent: Node) -> None: 
        new_children: list[Node] = []
        buffer: list[Node] = []
        break_buffer: list[Node] = []

        def flush_buffer():
            if buffer:
                table_node = Node("Table")
                for row in buffer:
                    table_node.link(row)
                new_children.extend(break_buffer)  # add preceding breaks
                new_children.append(table_node)
                buffer.clear()
                break_buffer.clear()
            elif break_buffer:
                new_children.extend(break_buffer)
                break_buffer.clear()

        for child in parent.children:
            # Recurse first
            self._collapse_tables(child)

            if child.kind == "TableRow":
                buffer.append(child)
            elif child.kind == "Break":
                break_buffer.append(child)
            else:
                flush_buffer()
                new_children.append(child)

        flush_buffer()
        parent.children = new_children
 
import re

class CSTNode:
    def __init__(self, children: list[CSTNode] | None = None):
        self.children = children or []
        self.is_syntax = False 
        
    def dump(self) -> str:
        return ''.join(child.dump() for child in self.children)

    def link(self, node: CSTNode):
        self.children.append(node)

def sanitize_latex(s: str) -> str: 
    replacements = {
        '\\': r'\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    pattern = re.compile('|'.join(re.escape(k) for k in replacements))
    return pattern.sub(lambda m: replacements[m.group()], s)
 

class TextNode(CSTNode):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
        
    def dump(self) -> str:
        return sanitize_latex(self.text)
    
class Title(CSTNode):
    def dump(self) -> str:
        return f"\\section{{{super().dump().strip()}}}\n"

class Section(CSTNode):
    def dump(self) -> str:
        return f"\\section{{{super().dump().strip()}}}\n"

class Subsection(CSTNode):
    def dump(self) -> str:
        return f"\\subsection{{{super().dump().strip()}}}\n"

class Bold(CSTNode):
    def dump(self) -> str:
        return f"\\textbf{{{super().dump()}}}"

class Italic(CSTNode):
    def dump(self) -> str:
        return f"\\textit{{{super().dump()}}}"

class MathBlock(CSTNode):
    def dump(self) -> str: 
        return f"\\begin{{equation}}\n{super().dump().strip()}\n\\end{{equation}}\n"

class MathInline(CSTNode):
    def dump(self) -> str:
        return f"${super().dump().strip()}$"

class CodeBlock(CSTNode):
    def dump(self) -> str:
        return f"\\begin{{verbatim}}\n{super().dump().strip()}\n\\end{{verbatim}}\n"

class CodeInline(CSTNode):
    def dump(self) -> str:
        return f"\\texttt{{{super().dump()}}}"

class List(CSTNode):
    def dump(self) -> str:
        content = ''.join(child.dump() for child in self.children).strip()
        return f"\\begin{{itemize}}\n{content}\\end{{itemize}}\n"

class Item(CSTNode):
    def dump(self) -> str:
        return f"\\item {super().dump().strip()}\n"
 
class Table(CSTNode):
    def dump(self) -> str:
        if not self.children:
            return ''
        # determine number of columns from first row
        first_row = self.children[0]
        n_cols = sum(1 for c in first_row.children if not getattr(c, 'is_syntax', False))
        col_fmt = ' | '.join(['l'] * n_cols)
        content = '\n'.join(child.dump() for child in self.children)
        return f"\\begin{{tabular}}{{{col_fmt}}}\n{content}\n\\end{{tabular}}\n"

class TableRow(CSTNode):   
    def dump(self) -> str: 
        parts = [c.dump().strip() for c in self.children if not c.is_syntax]
        if not parts:
            return ''
        return ' & '.join(parts) + r' \\'

class Figure(CSTNode):

    def __init__(self):
        super().__init__()
        self.caption = None
        self.label   = None

    def dump(self) -> str: 
        elements = [c.dump().strip() for c in self.children if not c.is_syntax and c.dump().strip()]
        url = elements[-1] if len(elements) > 1 else "" 
        return f"\\begin{{figure}}[h]\n\\centering\n\\includegraphics{{{url}}}\n\\end{{figure}}\n"
 
class Break(CSTNode):
    def dump(self) -> str:
        return "\n"

class List(CSTNode):
    def dump(self) -> str:
        if not self.children:
            return ''
        content = ''.join(child.dump() for child in self.children)
        return f"\\begin{{itemize}}\n{content}\\end{{itemize}}\n"

class Item(CSTNode):
    def dump(self) -> str:
        # Strip trailing whitespace, handle inline nodes properly
        return f"\\item {super().dump().strip()}\n"

class TableRow(CSTNode):
    def dump(self) -> str:
        parts = []
        cell_buffer: list[CSTNode] = []

        for c in self.children:
            if isinstance(c, ColumnSeparator):
                # End current cell
                parts.append(''.join(child.dump() for child in cell_buffer))
                cell_buffer.clear()
            else:
                cell_buffer.append(c)

        # Add last cell
        if cell_buffer:
            parts.append(''.join(child.dump() for child in cell_buffer))

        return ' & '.join(parts) + r' \\'

class ColumnSeparator(CSTNode):
    def __init__(self):
        super().__init__()
        self.is_syntax = True
    def dump(self) -> str:
        return ' & '

class Figure(CSTNode):
    def dump(self) -> str:
        # Look for URL and optional caption
        url = ''
        caption = ''
        for child in self.children:
            text = child.dump().strip()
            if text.startswith('http'):
                url = text
            else:
                caption += text
        return f"\\begin{{figure}}[h]\n\\centering\n\\includegraphics{{{url}}}\n\\caption{{{caption}}}\n\\end{{figure}}\n"


def ast_to_cst(node: Node) -> CSTNode:
    syntax_kinds = {'UrlSeparator', 'ColumnSeparator', 'FIG_MID', 'PIPE'}

    kind_map = {
        'Document': CSTNode,
        'Title': Title,
        'Section': Section,
        'Subsection': Subsection,
        'Bold': Bold,
        'Italic': Italic,
        'Math[Block]': MathBlock,
        'Math[Inline]': MathInline,
        'Math[Content]': TextNode,
        'Code[Block]': CodeBlock,
        'Code[Inline]': CodeInline,
        'Code[Content]': TextNode,
        'Item': Item,
        'Table': Table,
        'TableRow': TableRow,
        'Figure': Figure,
        'Break': Break,
        'Text': TextNode,
        'ColumnSeparator': ColumnSeparator,
        'List': List
    }

    # Syntax markers are ignored in CST
    if node.kind in syntax_kinds:
        cst_node = CSTNode()
        cst_node.is_syntax = True
        return cst_node

    cls = kind_map.get(node.kind, TextNode)

    # Text nodes
    if cls is TextNode:
        return TextNode(node.value or '')

    # TableRow needs to collect child cells properly
    if node.kind == 'TableRow':
        cst_node = TableRow()
        for child in node.children:
            child_cst = ast_to_cst(child)
            if getattr(child_cst, 'is_syntax', False):
                continue
            cst_node.link(child_cst)
        return cst_node

    # Table collects TableRow children
    if node.kind == 'Table':
        cst_node = Table()
        for child in node.children:
            if child.kind == 'TableRow':
                cst_node.link(ast_to_cst(child))
        return cst_node

    # Default for other nodes
    cst_node = cls()

    i = 0
    while i < len(node.children):
        child = node.children[i]

        # Wrap consecutive items into List
        if child.kind == 'Item':
            list_node = List()
            while i < len(node.children) and node.children[i].kind == 'Item':
                list_node.link(ast_to_cst(node.children[i]))
                i += 1
            cst_node.link(list_node)
            continue
        else:
            cst_node.link(ast_to_cst(child))
        i += 1

    return cst_node


from io import StringIO

if __name__ == '__main__':

    example = StringIO(r"""
# Title
                       
This is an example with **bold and *italic*** emphasis. 
                       
## Section

Inline math like $f(x) = x**2$ and math blocks:
                       
$$
f(x,y,z) = x*y + y*z + z*x,
$$
                       
where:
- $f$ is a **function**,
- and $x$, $y$, $z$ are variables.
                                                
### Subsection here

Inline `code` and code blocks:
                       
```
def square(x):
    return x**2
```

| Header 1 | Header 2   |
| -------- | ---------- |
| Cell $1$ | Cell **2** | 

Here is an image for the document:
![A cool landscape](https://example.com/image.png) 
                       
""")

lexicon = Lexicon([

    Rule('ENDL', r'(\n)', '\n'),
 
    Rule('H4', r'(^####)(?:\s*)(.*?)(\n|$)', '####'),
    Rule('H3', r'(^###)(?:\s*)(.*?)(\n|$)', '###'),
    Rule('H2', r'(^##)(?:\s)(.*?)(\n|$)', '##'), 
    Rule('H1', r'(^#)(?:\s)(.*?)(\n|$)', '#'),

    Rule('ITEM', r'(^[-\*])(?:\s+)(.*?)(\n|$)', '-'),

    Rule('ROW_START', r'(^\|)', '|'),
    Rule('ROW_END', r'(\|)(?=\s*\n|$)', '|'),
    Rule('PIPE', r'(\|)', '|'),
 
    Rule('FIG_OPEN', r'(\!\[)', '!['),
    Rule('FIG_MID', r'(\]\()', ']('),
    Rule('CLOSE_PAREN', r'(\))', ')'),
    
    Rule('STAR', r'(\*\*)(.*?)(\*\*)(?!\*)', '**'),
    Rule('STAR', r'(\*)(.*?)(\*)', '*'),
    Rule('SIGN', r'(\$\$)', '$$' ,'MATH'),
    Rule('SIGN', r'(\$)(.*?)(\$)', '$' ,'MATH'), 
    Rule('TICK', r'(\```)', '```' ,'CODE'),
    Rule('TICK', r'(\`)', '`' ,'CODE')
])

scanner = Scanner(lexicon)
grammar = Grammar( 
    productions=[   
        Production('Title',        ['H1', '#',   'ENDL', '\n']),
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
        'FIG_MID': 'UrlSeparator',
        'CLOSE_PAREN': 'Text',
        'PIPE': 'ColumnSeparator',
    }
)
 
parser = Parser(grammar) 

tokens = scanner.scan(example)   

ast = parser.parse(tokens) 
analyzer = Analyzer(ast)
ast = analyzer.analyze()

 
print(ast) 

cst_root = ast_to_cst(ast)   
latex_cst = cst_root.dump() 

print(latex_cst)