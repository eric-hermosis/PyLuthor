from luthor.lexing import Lexeme, Lexicon
 
def test_digits():
    number = Lexeme(r"\d+", "number")
    text = "Order 123 shipped"
    match = number.match(text, 6)
    assert match is not None
    assert match.group() == "123"

def test_punctuation():
    punctuation = Lexeme(r"[.!?]", "punctuation")
    text = "Hello!"
    match = punctuation.match(text, 5)
    assert match is not None
    assert match.group() == "!"