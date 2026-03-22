from __future__ import annotations
import re
from luthor.parser import Node

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
#        text = sanitize_latex(self.text)
        text = self.text
        text = re.sub(r'[\u200B\u200C\u200D\uFEFF]', '', text)
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
  
    def make_node(kind: str, value: str | None) -> CSTNode:
        cls = kind_map.get(kind)

        if cls is None:
            return TextNode(value or '')
 
        if cls is TextNode:
            return TextNode(value or '')
 
        return cls()
 
    if node.kind in syntax_kinds:
        n = CSTNode()
        n.is_syntax = True
        return n


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
 
        for i in range(len(node.children) - 2):
            a, b, c = node.children[i:i+3]
            if a.kind == 'Text' and b.kind == 'UrlSeparator' and c.kind == 'Text':
                fig.url = (c.value or '').strip()
                break

        return fig
 
    if node.kind == 'TableRow':
        row = TableRow()

        for child in node.children:
            c = ast_to_cst(child)

            if getattr(c, 'is_syntax', False) and not isinstance(c, ColumnSeparator):
                continue

            row.link(c)

        return row
 
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
 
    cst_node = make_node(node.kind, node.value)
 
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