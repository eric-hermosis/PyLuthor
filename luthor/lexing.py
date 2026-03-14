from re import Pattern, Match
from re import compile
from typing import List, Sequence 

class Lexeme: 
    pattern: Pattern[str] 
    lemma: str

    def __init__(self, words: str, lemma: str) -> None: 
        self.lemma = lemma 
        self.pattern = compile(words)

    def match(self, chunk: str, position: int) -> Match[str] | None:
        return self.pattern.match(chunk, position)

class Lexicon:
    rules: List[Lexeme]

    def __init__(self, rules: Sequence[Lexeme]):
        self.rules = list(rules)