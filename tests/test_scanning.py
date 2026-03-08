from pytest import fixture
from luthor.lexing import Lexer, Lexicon, Rule, Feature
from luthor.scanning import Scanner
from re import compile

@fixture
def equation() -> str:
    return r"""
$$
E = mc^2
$$
""" 

def test_scanning(equation):
    assert equation == r"""
$$
E = mc^2
$$
""" 
    lexicon = Lexicon([
        Rule(Feature('SIGN', 'MATH'), compile(r'\$+'))
    ])
    lexer   = Lexer(lexicon)
    scanner = Scanner(lexer)