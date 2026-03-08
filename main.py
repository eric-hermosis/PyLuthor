from luthor.lexing import Lexer, Lexicon, Rule, Feature
from luthor.scanning import Scanner
from re import compile
from io import StringIO

equation = StringIO(r"""
$$
E = mc^2
$$
""")
lexicon = Lexicon([
    Rule(Feature('SIGN', 'MATH'), compile(r'\$+'))
])
lexer   = Lexer(lexicon)
scanner = Scanner(lexer)
for token in scanner.scan(equation):
    print(token)