from luthor.lexing import Lexeme, Lexicon
from luthor.scanning import Scanner
from io import StringIO

if __name__ == '__main__':
 
    example = StringIO(r"""
### Title
                       
This is **bold**, *italic* and **bold and *italic***, can 
display inline equations $E = mc^2$, or blocks like:

$$
E = x*y + y*z + z*x
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

    for token in scanner.scan(example): 
        print(token)
