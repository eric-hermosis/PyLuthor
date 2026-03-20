from __future__ import annotations
from luthor.scanning import Scanner, Lexicon, Rule
from luthor.parsing import Parser, Grammar, Production, Node

class CSTNode:
    def __init__(self, children: list[CSTNode] | None = None):
        self.children = children or []
        self.is_syntax = False  # Flag to mark tokens like '|' or ']'

    def dump(self) -> str:
        # Recursive base: join all children's dumps
        return ''.join(child.dump() for child in self.children)

    def link(self, node: CSTNode):
        self.children.append(node)

import re

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
        # Use begin{equation} as requested
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

class Item(CSTNode):
    def dump(self) -> str:
        return f"\\item {super().dump().strip()}\n"

class TableRow(CSTNode):
    def dump(self) -> str: 
        parts = [c.dump().strip() for c in self.children if not c.is_syntax]
        if not parts:
            return ''
        return ' & '.join(parts) + r' \\'

class Figure(CSTNode):
    def dump(self) -> str: 
        elements = [c.dump().strip() for c in self.children if not c.is_syntax and c.dump().strip()]
        caption = elements[0] if len(elements) > 0 else ""
        url = elements[-1] if len(elements) > 1 else ""
        return f"\\begin{{figure}}[h]\n\\centering\n\\includegraphics{{{url}}}\n\\caption{{{caption}}}\n\\end{{figure}}\n"

class Break(CSTNode):
    def dump(self) -> str:
        return "\n"

def ast_to_cst(node: Node) -> CSTNode:
    # Tokens we want to traverse but not print literally in the dump
    syntax_kinds = {'UrlSeparator', 'ColumnSeparator', 'FIG_MID', 'PIPE'}

    # Map AST node kinds to CST node classes
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
        'TableRow': TableRow,
        'Figure': Figure,
        'Break': Break,
        'Text': TextNode,
    }

    # If this node is a syntax marker, always use plain CSTNode
    if node.kind in syntax_kinds:
        cst_node = CSTNode()
        cst_node.is_syntax = True
    else:
        cls = kind_map.get(node.kind, TextNode)
        if cls is TextNode:
            return TextNode(node.value or '')
        cst_node = cls()

    # Recursively link children
    for child in node.children:
        cst_node.link(ast_to_cst(child))

    return cst_node
from io import StringIO

if __name__ == '__main__':

    example = StringIO(r"""
# Title
                       
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

This is an example with **bold and *italic*** emphasis. 

| Header 1 | Header 2   |
| -------- | ---------- |
| Cell $1$ | Cell **2** |

Here is an image for the document:
![A cool landscape](https://example.com/image.png)
                       
""")

lexicon = Lexicon([

    Rule('ENDL', r'(\n)', '\n'),
 
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
    Rule('TICK', r'(\`)', '`' ,'CODE'),  
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
print(ast)

cst_root = ast_to_cst(ast)   
latex_cst = cst_root.dump() 

print(latex_cst)