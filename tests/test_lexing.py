from re import compile
from luthor.lexing import Rule, Feature

def test_rule(): 
    past_tense = Rule(
        feature=Feature(name='tense', phrase='past'),
        pattern=compile(r".*"),
        transform= lambda word: [word + 'd' if word.endswith('e') else word + 'ed']
    )

    assert past_tense.transform('love') == ['loved'] 
    assert past_tense.transform('walk') == ['walked'] 