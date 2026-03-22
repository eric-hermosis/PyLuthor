from __future__ import annotations
from typing import Generator, List 
from collections import deque
from luthor.markdown.scanner import Token

class Node:
    children: List[Node]
    def __init__(self, name: str, value: str = ""):
        self.name = name
        self.value = value
        self.children = []

    def __repr__(self, level=0) -> str:
        indent = "  " * level
        val = f" {repr(self.value.strip())}" if self.value.strip() else ""
        out = f"{indent}{self.name}{val}\n"
        for child in self.children:
            out += child.__repr__(level + 1)
        return out
    
class Parser:
    def __init__(self): 
        self.queue = deque()
        self.rules = {
            'HEAD':  {'node': 'Header',     'closes_on': ['ENDL']},
            'ITEM':  {'node': 'ListItem',   'closes_on': ['ENDL']},
            'QUOTE': {'node': 'BlockQuote', 'closes_on': ['ENDL']},
            'EMPH':  {'node': 'Emphasis',   'toggle': True},
            'MATH':  {'node': 'MathBlock',  'toggle': True},
            'CODE':  {'node': 'CodeBlock',  'toggle': True},
        }
        self.stack: List[Node] = [Node("DocumentRoot")]

    def parse(self, token: Token) -> Generator[Node, None, None]: 
        self.queue.append(token)
        yield from self._process_queue()

    def flush(self) -> Generator[Node, None, None]: 
        yield from self._process_queue(force_flush=True)

    def _process_queue(self, force_flush: bool = False) -> Generator[Node, None, None]:
        while self.queue:
            token = self.queue.popleft()
             
            if token.name == 'TEXT' and not token.value.strip():
                continue

            current_node = self.stack[-1]
 
            active_rule = next((r for r in self.rules.values() if r.get('node') == current_node.name), None)
            if active_rule and token.name in active_rule.get('closes_on', []):
                finished_node = self.stack.pop()
                if len(self.stack) == 1:
                    yield finished_node
                continue
 
            rule = self.rules.get(token.name)
            
            if rule and rule.get('toggle'):
                if current_node.name == rule['node']:
                    finished_node = self.stack.pop()  
                    if len(self.stack) == 1:
                        yield finished_node
                else:
                    new_node = Node(rule['node'])  
                    current_node.children.append(new_node)
                    self.stack.append(new_node)
                    
            elif rule:
                new_node = Node(rule['node'], token.value)
                current_node.children.append(new_node)
                self.stack.append(new_node)
                
            else: 
                if token.name == 'ENDL' and len(self.stack) == 1:
                    continue  
                    
                leaf = Node(token.name, token.value)
                current_node.children.append(leaf)

        if force_flush:
            while len(self.stack) > 1:
                yield self.stack.pop()


import unicodedata 
import re

class DeprecatedParser:
    """Handles parsing and converting Markdown text to LaTeX."""
    
    def sanitize_unicode(self, text: str) -> str:
        return text.replace("\u200B", "")

    def sanitize_latex(self, s: str) -> str:
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
        for char, rep in replacements.items():
            s = s.replace(char, rep)
        return s

    def sanitize_label(self, s: str) -> str:
        s = ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))
        s = re.sub(r'[^0-9a-zA-Z_-]', '', s)
        return s

    def strip_title(self, text: str) -> str:
        return re.sub(r"^\s*#\s+.*\n+", "", text)

    def strip_citation_section(self, text: str) -> str:
        return re.sub(r"\n##\s+Citation[\s\S]*$", "", text)
 
    def convert_math(self, text: str):
        equations = []
        def repl(m):
            eq = m.group(1).strip()
            token = f"@@EQ{len(equations)}@@"
            equations.append(eq)
            return token
        text = re.sub(r"\$\$(.*?)\$\$", repl, text, flags=re.S)
        return text, equations

    def restore_math(self, text: str, equations):
        for i, eq in enumerate(equations):
            text = text.replace(f"@@EQ{i}@@", "\\begin{equation}\n" + eq + "\n\\end{equation}")
        return text

    def convert_sections(self, text: str) -> str:
        levels = [("####", r"\subsubsection*{"), ("###", r"\subsection*{"), ("##", r"\section*{"), ("#", r"\section*{")]
        for markdown, latex in levels:
            text = re.sub(
                rf"^\s*{re.escape(markdown)}\s+(.*)$",
                lambda m, l=latex: l + self.sanitize_latex(m.group(1)) + "}",
                text, flags=re.M)
        return text

    def convert_lists(self, text: str) -> str:
        lines = text.splitlines()
        out = []
        in_list = False

        for line in lines:
            if re.match(r"^\s*-\s+", line):
                if not in_list:
                    out.append(r"\begin{itemize}")
                    in_list = True
                out.append(r"  \item " + line.lstrip("- ").strip())
            elif in_list and line.strip() == "":
                continue
            else:
                if in_list:
                    out.append(r"\end{itemize}")
                    in_list = False
                out.append(line)

        if in_list:
            out.append(r"\end{itemize}")

        return "\n".join(out)

    def convert_inline_formatting(self, text: str) -> str:
        text = re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", text)
        text = re.sub(r"(?<!\w)\*(.*?)\*(?!\w)", r"\\emph{\1}", text)
        text = re.sub(r"(?<!\w)_(.*?)_(?!\w)", r"\\emph{\1}", text)
        text = re.sub(r"`(.*?)`", r"\\texttt{\1}", text)
        return text

    def convert_citations(self, text: str) -> str:
        return re.sub(r"\[@([^\]]+)\]", lambda m: m.group(0) if m.group(1).startswith("fig:") else f"\\cite{{{m.group(1)}}}", text)

    def convert_fig_refs(self, text: str) -> str:
        return re.sub(r"\[@fig:([^\]]+)\]", r"\\ref{fig:\1}", text)

    def convert_images(self, text: str) -> str:
        lines = text.splitlines()
        out = []
        i = 0
        img_pattern = re.compile(r"!\[\{#([^\}]+)\}\]\((.*?)\)")

        while i < len(lines):
            line = lines[i].strip()
            m = img_pattern.match(line)

            if m:
                label = m.group(1)
                path = m.group(2)
                caption = ""
                j = i + 1

                while j < len(lines):
                    if lines[j].strip():
                        caption = lines[j].strip()
                        break
                    j += 1

                out.append(r"\begin{figure}[h]")
                out.append(r"  \centering")
                out.append(rf"  \includegraphics[width=1.0\textwidth]{{{path}}}")
                out.append(rf"  \caption{{{caption}}}")
                out.append(rf"  \label{{{label}}}")
                out.append(r"\end{figure}")

                i = j + 1
                continue

            out.append(lines[i])
            i += 1

        return "\n".join(out)

    def convert_tables(self, text: str) -> str:
        def md_table_to_latex(table_md, caption="", label=""):
            lines = table_md.strip().splitlines()
            if len(lines) < 2:
                return table_md

            headers = [h.strip() for h in lines[0].split("|")[1:-1]]
            col_format = " | ".join(["l"] * len(headers))

            latex = [
                r"\begin{table}[h]",
                r"  \centering",
                f"  \\begin{{tabular}}{{{col_format}}}",
                "  \\hline"
            ]

            latex.append(" & ".join(headers) + " \\\\ \\hline")

            for row in lines[2:]:
                cells = [c.strip() for c in row.split("|")[1:-1]]
                processed_cells = []
                for cell in cells:
                    if cell.startswith("$") and cell.endswith("$"):
                        processed_cells.append(cell)
                    else:
                        processed_cells.append(self.sanitize_latex(cell))
                latex.append("  " + " & ".join(processed_cells) + " \\\\")

            latex.append("  \\hline\n  \\end{tabular}")

            if caption:
                latex.append(f"  \\caption{{{caption}}}")
            if label:
                latex.append(f"  \\label{{table:{label}}}")

            latex.append(r"\end{table}")
            return "\n".join(latex)

        def table_repl(match):
            table_md = match.group(1)
            caption_label_match = re.search(r"\s*(.*)", table_md, re.S)
            caption, label = "", ""

            if caption_label_match:
                label = self.sanitize_label(caption_label_match.group(1))
                caption = caption_label_match.group(2).strip()
                table_md = re.sub(r".*", "", table_md, flags=re.S)

            return md_table_to_latex(table_md, caption=caption, label=label)

        table_pattern = r"((?:\|.*\|\n)+(?:.*)?)"
        return re.sub(table_pattern, table_repl, text)

    def convert_table_refs(self, text: str) -> str:
        return re.sub(r"\[@tab:([^\]]+)\]", r"\\ref{table:\1}", text)

    def markdown_to_latex(self, text: str) -> str: 
        text = self.sanitize_unicode(text)  
        text = self.convert_fig_refs(text)
        text = self.convert_table_refs(text)
        text = self.convert_citations(text) 
        text, equations = self.convert_math(text)
        text = self.convert_inline_formatting(text)
        text = self.convert_sections(text)
        text = self.convert_lists(text)
        text = self.convert_tables(text)
        text = self.convert_images(text)
        text = self.restore_math(text, equations)
        return text