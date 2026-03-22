from __future__ import annotations

from typing import Iterator, Generator
from typing import Sequence  
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
        self._attach_metadata(self.root)
        return self.root

    # -------------------------
    # TABLE COLLAPSE
    # -------------------------
    def _collapse_tables(self, parent: Node) -> None: 
        new_children: list[Node] = []
        buffer: list[Node] = []
        break_buffer: list[Node] = []

        def flush_buffer():
            if buffer:
                table_node = Node("Table")
                for row in buffer:
                    table_node.link(row)
                new_children.extend(break_buffer)
                new_children.append(table_node)
                buffer.clear()
                break_buffer.clear()
            elif break_buffer:
                new_children.extend(break_buffer)
                break_buffer.clear()

        for child in parent.children:
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
        
    def _attach_metadata(self, parent: Node) -> None:
        import re

        meta_re = re.compile(
            r'(?s)^(?P<prefix>.*?)<!--(?P<kind>table|figure):(?P<label>.+?)-->(?P<suffix>.*)$'
        )

        new_children: list[Node] = []
        i = 0

        while i < len(parent.children):
            node = parent.children[i]
            self._attach_metadata(node)

            if node.kind == 'Text' and node.value:
                m = meta_re.match(node.value)
                if m:
                    prefix = m.group('prefix')
                    kind = m.group('kind')
                    label = m.group('label').strip()
                    suffix = m.group('suffix').strip()

                    # keep any text before the comment
                    if prefix.strip():
                        new_children.append(Node('Text', prefix))

                    # find previous target node
                    j = len(new_children) - 1
                    while j >= 0 and new_children[j].kind == 'Break':
                        j -= 1
                    target = new_children[j] if j >= 0 else None

                    if target and (
                        (kind == 'table' and target.kind == 'Table') or
                        (kind == 'figure' and target.kind == 'Figure')
                    ):
                        target.value = label

                        # caption comes from the same node, right after the comment
                        if suffix:
                            target.caption = suffix
                        else:
                            # fallback: immediate next text node after breaks only
                            k = i + 1
                            while k < len(parent.children) and parent.children[k].kind == 'Break':
                                k += 1
                            if k < len(parent.children):
                                candidate = parent.children[k]
                                if candidate.kind == 'Text' and candidate.value and candidate.value.strip():
                                    target.caption = candidate.value.strip()
                                    i = k  # consume caption node

                        i += 1
                        continue

            new_children.append(node)
            i += 1

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
        '~': r'\textasciitilde{}', 
    }
    pattern = re.compile('|'.join(re.escape(k) for k in replacements))
    return pattern.sub(lambda m: replacements[m.group()], s)
 

class DocumentNode(CSTNode):
    def dump(self) -> str: 
        raw = super().dump() 
        parts = re.split(r'(\\begin\{verbatim\}.*?\\end\{verbatim\})', raw, flags=re.DOTALL)
        
        for i in range(len(parts)):
            if not parts[i].startswith('\\begin{verbatim}'): 
                parts[i] = re.sub(r'\n{3,}', '\n\n', parts[i])
                 
        return "".join(parts).strip() + '\n'

class TextNode(CSTNode):
    def __init__(self, text: str):
        super().__init__()
        self.text = text
 
    def dump(self) -> str:
        text = sanitize_latex(self.text)

        def repl(match):
            text_part = match.group(1)
            target = match.group(2)
 
            if re.match(r'(table|figure):', target):
                return f"\\ref{{{target}}}"
 
            return f"\\href{{{target}}}{{{text_part}}}" 
        return re.sub(r'\[(.*?)\]\((.*?)\)', repl, text)
    
class Title(CSTNode):
    def dump(self) -> str:
        return f"\\section{{{super().dump().strip()}}}\n"

class Section(CSTNode):
    def dump(self) -> str:
        return f"\\subsection{{{super().dump().strip()}}}\n"

class Subsection(CSTNode):
    def dump(self) -> str:
        return f"\\subsubsection{{{super().dump().strip()}}}\n"

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
class Figure(CSTNode):
    def __init__(self):
        super().__init__()
        self.caption = None
        self.label = None
        self.url = None

    def dump(self) -> str:
        res = "\\begin{figure}[h]\n\\centering\n"

        if self.url:
            res += f"\\includegraphics{{{self.url}}}\n"
        else:
            res += "\\includegraphics{}\n"

        if self.caption:
            res += f"\\caption{{{self.caption}}}\n"

        if self.label:
            res += f"\\label{{{self.label}}}\n"

        res += "\\end{figure}\n"
        return res
    
class Break(CSTNode):
    def dump(self) -> str:
        return "\n" 

class ColumnSeparator(CSTNode):
    def __init__(self):
        super().__init__()
        self.is_syntax = True
        
    def dump(self) -> str:
        return ' & '

class Table(CSTNode):
    def __init__(self):
        super().__init__()
        self.caption = None
        self.label = None

    def dump(self) -> str:
        if not self.children:
            return ''
            
        first_row = self.children[0]
        n_cols = sum(1 for c in first_row.children if isinstance(c, ColumnSeparator)) + 1
        col_fmt = ' | '.join(['l'] * n_cols)
        content = '\n'.join(child.dump() for child in self.children)
        
        tabular_block = f"\\begin{{tabular}}{{{col_fmt}}}\n{content}\n\\end{{tabular}}\n"
        if not self.caption and not self.label:
            return tabular_block
            
        res = "\\begin{table}[h]\n\\centering\n"
        res += tabular_block
        
        if self.caption:
            res += f"\\caption{{{self.caption}}}\n"
            
        if self.label:
            res += f"\\label{{{self.label}}}\n" 
        res += "\\end{table}\n" 
        return res

class TableRow(CSTNode):
    def dump(self) -> str:
        parts = []
        cell_buffer: list[CSTNode] = []

        for c in self.children:
            if isinstance(c, ColumnSeparator):
                parts.append(''.join(child.dump() for child in cell_buffer))
                cell_buffer.clear()
            else:
                cell_buffer.append(c)
        # Add last cell
        if cell_buffer:
            parts.append(''.join(child.dump() for child in cell_buffer))
        is_separator = all(part.strip().replace('-', '') == '' for part in parts)
        
        if is_separator and parts:
            return r'\hline'

        return ' & '.join(parts) + r' \\' 
 
class Reference(CSTNode):
    def __init__(self, label: str, text: str | None = None):
        super().__init__()
        self.label = label
        self.text = text   

    def dump(self) -> str: 
        return f"\\ref{{{self.label}}}"
    
class List(CSTNode):
    def dump(self) -> str:
        if not self.children:
            return ''
        content = ''.join(child.dump() for child in self.children)
        return f"\\begin{{itemize}}\n{content}\\end{{itemize}}\n"

class Item(CSTNode):
    def dump(self) -> str:
        return f"\\item {super().dump().strip()}\n" 
 
def ast_to_cst(node: Node) -> CSTNode:
    syntax_kinds = {'UrlSeparator', 'PIPE'}

    kind_map = {
        'Document': DocumentNode,
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
        'List': List,
    }

    # -------------------------
    # FACTORY (THIS FIXES EVERYTHING)
    # -------------------------
    def make_node(kind: str, value: str | None) -> CSTNode:
        cls = kind_map.get(kind)

        if cls is None:
            return TextNode(value or '')

        # value-carrying nodes
        if cls is TextNode:
            return TextNode(value or '')

        # all others: no-arg ctor
        return cls()

    # -------------------------
    # IGNORE SYNTAX
    # -------------------------
    if node.kind in syntax_kinds:
        n = CSTNode()
        n.is_syntax = True
        return n

    # -------------------------
    # LINK
    # -------------------------
    if node.kind == 'Link':
        if len(node.children) >= 3:
            a, b, c = node.children[:3]
            if a.kind == 'Text' and b.kind == 'UrlSeparator' and c.kind == 'Text':
                target = c.value
                if target and target.startswith(('table:', 'figure:')):
                    return Reference(label=target)
                else:
                    n = CSTNode()
                    n.link(TextNode(a.value or ''))
                    return n
        return TextNode('')


    if node.kind == 'Figure':
        fig = Figure()

        if node.value:
            fig.label = f"figure:{node.value}"
 
        fig.caption = getattr(node, "caption", None)

        # only extract the image URL from the figure syntax
        for i in range(len(node.children) - 2):
            a, b, c = node.children[i:i+3]
            if a.kind == 'Text' and b.kind == 'UrlSeparator' and c.kind == 'Text':
                fig.url = (c.value or '').strip()
                break

        return fig

    # -------------------------
    # TABLE ROW
    # -------------------------
    if node.kind == 'TableRow':
        row = TableRow()

        for child in node.children:
            c = ast_to_cst(child)

            if getattr(c, 'is_syntax', False) and not isinstance(c, ColumnSeparator):
                continue

            row.link(c)

        return row

    # -------------------------
    # TABLE
    # -------------------------
    if node.kind == 'Table':
        table = Table()

        if node.value:
            table.label = f"table:{node.value}"

        # carry metadata attached by Analyzer
        table.caption = getattr(node, "caption", None)

        for child in node.children:
            if child.kind == 'TableRow':
                table.link(ast_to_cst(child))

        return table

    # -------------------------
    # DEFAULT NODE CREATION
    # -------------------------
    cst_node = make_node(node.kind, node.value)

    # -------------------------
    # CHILDREN
    # -------------------------
    i = 0
    while i < len(node.children):
        child = node.children[i]

        # GROUP LIST ITEMS
        if child.kind == 'Item':
            lst = List()

            while i < len(node.children) and node.children[i].kind == 'Item':
                lst.link(ast_to_cst(node.children[i]))
                i += 1

            cst_node.link(lst)
            continue

        cst_node.link(ast_to_cst(child))
        i += 1

    return cst_node 
 
from io import StringIO

if __name__ == '__main__':

    example = StringIO(r"""
# Section

This is an example with **bold and *italic* emphasis** and *italic and **bold** emphasis*.

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
  



lexicon = Lexicon([ 
    Rule('ENDL', r'(\n)', '\n'), 
    Rule('H4', r'(^####)(?:\s*)(.*?)(\n|$)', '####'),
    Rule('H3', r'(^###)(?:\s*)(.*?)(\n|$)', '###'),
    Rule('H2', r'(^##)(?:\s)(.*?)(\n|$)', '##'),
    Rule('H1', r'(^#)(?:\s)(.*?)(\n|$)', '#'),
    Rule('LINK', r'(\[)(.*?)(\]\()(.*?)(\))', '['),
    Rule('ITEM', r'(^[-\*])(?:\s+)(.*?)(\n|$)', '-'),

    Rule('ROW_START', r'(^\|)', '|'),
    Rule('ROW_END', r'(\|)(?=\s*\n|$)', '|'),
    Rule('PIPE', r'(\|)', '|'),
 
    Rule('FIG_OPEN', r'(\!\[)', '!['),
    Rule('FIG_SEP', r'(\]\()', ']('),
    Rule('CLOSE_PAREN', r'(\))', ')'),

    Rule('STAR', r'(\*\*)(.*?)(\*\*)(?!\*)', '**'),
    Rule('STAR', r'(\*)(.*?)(\*)', '*'),
    Rule('SIGN', r'(\$\$)', '$$', 'MATH'),
    Rule('SIGN', r'(\$)(.*?)(\$)', '$', 'MATH'),
    Rule('TICK', r'(\```)', '```', 'CODE'),
    Rule('TICK', r'(\`)', '`', 'CODE'),
]) 

scanner = Scanner(lexicon)
grammar = Grammar( 
    productions=[   
        Production('Title',        ['H1', '#',   'ENDL', '\n']),
        Production('Link', ['LINK', '[', 'CLOSE_PAREN', ')']),
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
 
parser = Parser(grammar) 

tokens = scanner.scan(example)   

ast = parser.parse(tokens) 
analyzer = Analyzer(ast)
ast = analyzer.analyze()

 
print(ast) 

cst_root = ast_to_cst(ast)   
latex_cst = cst_root.dump() 

print(latex_cst)