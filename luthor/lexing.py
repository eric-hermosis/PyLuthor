from typing import Sequence 
from typing import List
from re import Pattern, Match 
from re import compile

class Rule:
    name: str
    pattern : Pattern[str]
    terminal: str
    category: str | None

    def __init__(self, name: str, pattern: str, terminal: str, category: str | None = None) -> None:
        self.name = name
        self.pattern  = compile(pattern)
        self.terminal = terminal
        self.category = category

    def match(self, chunk: str, position: int = 0) -> Match[str] | None: 
        return self.pattern.match(chunk, position)  
 
class Lexicon:
    rules: List[Rule]

    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = list(rules)