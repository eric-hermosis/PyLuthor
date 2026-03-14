from pytest import fixture
from luthor.lexing import Lexeme, Lexicon
from luthor.scanning import Scanner, Token
 
from io import StringIO

def test_scannig():

    example = StringIO(r"""
### Title
                       
This is **bold**, *italic* and **bold and *italic***, can 
display inline equations $E = mc^2$, or blocks like:

$$
E = \sqrt{(pc)^2 + (mc^2)^2},
$$


where:

- $E$ is energy,
- $p$ is momentum,
- and $c$ is speed of light.

It can display inline `code` or code blocks like:

```python 

def energy(p, m):
    return (p**2 + m**2)**0.5
```
"""
)
    lexicon = Lexicon([
        Lexeme(r'^#{1,6}', 'NUMBER SIGN'),
        Lexeme(r'\*{1,2}', 'ASTERISK'),
        Lexeme(r'^_', 'LOW LINE'),
        Lexeme(r'^-', 'HYPHEN-MINUS'),
        Lexeme(r'^\+', 'PLUS SIGN'),
        Lexeme(r'^>', 'GREATER-THAN SIGN'),
        Lexeme(r'`{1,6}', 'GRAVE ACCENT'),
        Lexeme(r'^~{2,3}', 'TILDE'),
        Lexeme(r'\[', 'LEFT SQUARE BRACKET'),
        Lexeme(r'\]', 'RIGHT SQUARE BRACKET'),
        Lexeme(r'\(', 'LEFT PARENTHESIS'),
        Lexeme(r'\)', 'RIGHT PARENTHESIS'),
        Lexeme(r'^!', 'EXCLAMATION MARK'),
        Lexeme(r'\|', 'VERTICAL LINE'),
        Lexeme(r':', 'COLON'),
        Lexeme(r'\n', 'LINE FEED'),
        Lexeme(r'\r', 'CARRIAGE RETURN'),
        Lexeme(r'\t', 'CHARACTER TABULATION'),
        Lexeme(r'\$', 'DOLLAR SIGN'),
        Lexeme(r'\.', 'FULL STOP'),
        Lexeme(r'\\', 'REVERSE SOLIDUS'),
        Lexeme(r'/', 'SOLIDUS'),
        Lexeme(r'"', 'QUOTATION MARK'),
        Lexeme(r"'", 'APOSTROPHE'),
    ])
        
    scanner = Scanner(lexicon)
   
    tokens = []

    for token in scanner.scan(example): 
        tokens.append(token)

    assert tokens == [
        Token('LINE FEED', '\n') ,
        Token('NUMBER SIGN', '###') ,
        Token('CONTENT', ' Title') ,
        Token('LINE FEED', '\n') ,
        Token('CONTENT', '                       ') ,
        Token('LINE FEED', '\n') ,
        Token('CONTENT', 'This is ') ,
        Token('ASTERISK', '**') ,
        Token('CONTENT', 'bold') ,
        Token('ASTERISK', '**') ,
        Token('CONTENT', ', ') ,
        Token('ASTERISK', '*') ,
        Token('CONTENT', 'italic') ,
        Token('ASTERISK', '*') ,
        Token('CONTENT', ' and ') ,
        Token('ASTERISK', '**') ,
        Token('CONTENT', 'bold and ') ,
        Token('ASTERISK', '*') ,
        Token('CONTENT', 'italic') ,
        Token('ASTERISK', '**') ,
        Token('ASTERISK', '*') ,
        Token('CONTENT', ', can ') ,
        Token('LINE FEED', '\n') ,
        Token('CONTENT', 'display inline equations ') ,
        Token('DOLLAR SIGN', '$') ,
        Token('CONTENT', 'E = mc^2') ,
        Token('DOLLAR SIGN', '$') ,
        Token('CONTENT', ', or blocks like') ,
        Token('COLON', ':') ,
        Token('LINE FEED', '\n') ,
        Token('LINE FEED', '\n') ,
        Token('DOLLAR SIGN', '$') ,
        Token('DOLLAR SIGN', '$') ,
        Token('LINE FEED', '\n') ,
        Token('CONTENT', 'E = ') ,
        Token('REVERSE SOLIDUS', '\\') ,
        Token('CONTENT', 'sqrt{') ,
        Token('LEFT PARENTHESIS', '(') ,
        Token('CONTENT', 'pc') ,
        Token('RIGHT PARENTHESIS', ')') ,
        Token('CONTENT', '^2 + ') ,
        Token('LEFT PARENTHESIS', '(') ,
        Token('CONTENT', 'mc^2') ,
        Token('RIGHT PARENTHESIS', ')') ,
        Token('CONTENT', '^2},') ,
        Token('LINE FEED', '\n') ,
        Token('DOLLAR SIGN', '$') ,
        Token('DOLLAR SIGN', '$') ,
        Token('LINE FEED', '\n') ,
        Token('LINE FEED', '\n') ,
        Token('LINE FEED', '\n') ,
        Token('CONTENT', 'where') ,
        Token('COLON', ':') ,
        Token('LINE FEED', '\n') ,
        Token('LINE FEED', '\n') ,
        Token('HYPHEN-MINUS', '-') ,
        Token('CONTENT', ' ') ,
        Token('DOLLAR SIGN', '$') ,
        Token('CONTENT', 'E') ,
        Token('DOLLAR SIGN', '$') ,
        Token('CONTENT', ' is energy,') ,
        Token('LINE FEED', '\n') ,
        Token('HYPHEN-MINUS', '-') ,
        Token('CONTENT', ' ') ,
        Token('DOLLAR SIGN', '$') ,
        Token('CONTENT', 'p') ,
        Token('DOLLAR SIGN', '$') ,
        Token('CONTENT', ' is momentum,') ,
        Token('LINE FEED', '\n') ,
        Token('HYPHEN-MINUS', '-') ,
        Token('CONTENT', ' and ') ,
        Token('DOLLAR SIGN', '$') ,
        Token('CONTENT', 'c') ,
        Token('DOLLAR SIGN', '$') ,
        Token('CONTENT', ' is speed of light') ,
        Token('FULL STOP', '.') ,
        Token('LINE FEED', '\n') ,
        Token('LINE FEED', '\n') ,
        Token('CONTENT', 'It can display inline ') ,
        Token('GRAVE ACCENT', '`') ,
        Token('CONTENT', 'code') ,
        Token('GRAVE ACCENT', '`') ,
        Token('CONTENT', ' or code blocks like') ,
        Token('COLON', ':') ,
        Token('LINE FEED', '\n') ,
        Token('LINE FEED', '\n') ,
        Token('GRAVE ACCENT', '```') ,
        Token('CONTENT', 'python ') ,
        Token('LINE FEED', '\n') ,
        Token('LINE FEED', '\n') ,
        Token('CONTENT', 'def energy') ,
        Token('LEFT PARENTHESIS', '(') ,
        Token('CONTENT', 'p, m') ,
        Token('RIGHT PARENTHESIS', ')') ,
        Token('COLON', ':') ,
        Token('LINE FEED', '\n') ,
        Token('CONTENT', '    return ') ,
        Token('LEFT PARENTHESIS', '(') ,
        Token('CONTENT', 'p') ,
        Token('ASTERISK', '**') ,
        Token('CONTENT', '2 + m') ,
        Token('ASTERISK', '**') ,
        Token('CONTENT', '2') ,
        Token('RIGHT PARENTHESIS', ')') ,
        Token('ASTERISK', '**') ,
        Token('CONTENT', '0') ,
        Token('FULL STOP', '.') ,
        Token('CONTENT', '5') ,
        Token('LINE FEED', '\n') ,
        Token('GRAVE ACCENT', '```') ,
        Token('LINE FEED', '\n') 
    ]