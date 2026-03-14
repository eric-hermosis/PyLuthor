from __future__ import annotations
from typing import List, Sequence
from collections import deque
from luthor.scanning import Token

class Node:
    type: str
    value: str | None
    children: List[Node]

    def __init__(self, type: str, value: str | None, children: Sequence[Node] | None = None):
        self.type  = type
        self.value = value
        self.children = list(children) if children else []

    def __repr__(self, level: int = 0) -> str:
        indent = "    " * level
        if not self.children:
            return f"{indent}Node({self.type!r}, {self.value!r}, [])"

        child_reprs = ",\n".join(c.__repr__(level + 1) for c in self.children)
        return f"{indent}Node({self.type!r}, {self.value!r}, [\n{child_reprs}\n{indent}])"


class Parser:

    def __init__(self):
        self.buffer  = deque() 

    def parse(self, token: Token):
        self.buffer.append(token)

    def peek(self, position: int = 0) -> Token | None:
        return self.buffer[position] if position < len(self.buffer) else None 

    def run(self, stop=None): 
        while True:
            token = self.peek()

            if token is None:
                break

            # Stop condition for nested constructs
            if stop and token.name == "ASTERISK" and token.value == stop:
                break

            # Text content
            if token.name == "CONTENT":
                self.buffer.popleft()
                yield Node("text", token.value)
                continue

            # Bold or italic
            if token.name == "ASTERISK":
                if token.value == "**":
                    self.buffer.popleft()
                    children = list(self.run(stop="**"))
                    closing = self.buffer.popleft()
                    if closing is None or closing.value != "**":
                        raise SyntaxError("Unclosed bold")
                    yield Node("bold", None, children)
                    continue

                if token.value == "*":
                    self.buffer.popleft()
                    children = list(self.run(stop="*"))
                    closing = self.buffer.popleft()
                    if closing is None or closing.value != "*":
                        raise SyntaxError("Unclosed italic")
                    yield Node("italic", None, children)
                    continue

            # Math: $ ... $ (inline) or $$ ... $$ (multiline)
            if token.name == "DOLLAR SIGN":
                self.buffer.popleft()
                next_token = self.peek()
                is_multiline = next_token and next_token.name == "DOLLAR SIGN" and next_token.value == "$"
                
                if is_multiline:
                    self.buffer.popleft()  # consume second $
                    math_content = []
                    while True:
                        t = self.peek()
                        if t is None:
                            raise SyntaxError("Unclosed multiline math")
                        # check for closing $$
                        if t.name == "DOLLAR SIGN":
                            peek_next = self.peek(1)
                            if peek_next and peek_next.name == "DOLLAR SIGN":
                                self.buffer.popleft()  # first $
                                self.buffer.popleft()  # second $
                                break
                        math_content.append(self.buffer.popleft().value)
                    yield Node("math_multiline", "".join(math_content))
                else:
                    # inline math
                    math_content = []
                    while True:
                        t = self.peek()
                        if t is None:
                            raise SyntaxError("Unclosed inline math")
                        if t.name == "DOLLAR SIGN" and t.value == "$":
                            break
                        math_content.append(self.buffer.popleft().value)
                    closing = self.buffer.popleft()  # consume closing $
                    yield Node("math_inline", "".join(math_content))
                continue

            raise SyntaxError(f"Unexpected token {token}")

def print_ast(node, indent=0):
    space = " " * indent
    print(f"{space}{node.type}")
    for child in node.children:
        if isinstance(child, Node):
            print_ast(child, indent + 2)
        else:
            print(f"{space}  {child!r}")


def main():
    parser = Parser()

    tokens = [
        Token("CONTENT", "This is "),           # normal text
        Token("ASTERISK", "**"),                # bold start
        Token("CONTENT", "bold"),               # bold content
        Token("ASTERISK", "**"),                # bold end
        Token("CONTENT", ", inline math "),     
        Token("DOLLAR SIGN", "$"),              # inline math start
        Token("CONTENT", "E=mc^2"),             
        Token("DOLLAR SIGN", "$"),              # inline math end
        Token("CONTENT", ", multiline math:\n"),
        Token("DOLLAR SIGN", "$"),              # multiline math start ($$)
        Token("DOLLAR SIGN", "$"),
        Token("CONTENT", "w"),
        Token("DOLLAR SIGN", "$"),              # multiline math end ($$)
        Token("DOLLAR SIGN", "$"),
        Token("CONTENT", "\nAnd finally, italic "),  
        Token("ASTERISK", "*"),                 # italic start
        Token("CONTENT", "italic"),             
        Token("ASTERISK", "*"),                 # italic end
    ]

    for token in tokens:
        parser.parse(token)

    ast = parser.run()

    print("AST:\n")
    for node in ast:
        print(node)


if __name__ == "__main__":
    main()