from typing import Generator
from typing import Sequence, List
from typing import Callable
from dataclasses import dataclass
from re import Pattern

@dataclass(frozen=True)
class Feature:
    name: str
    phrase: str | None = None

@dataclass(frozen=True)
class Rule:
    feature: Feature
    pattern: Pattern[str] 
    transform: Callable[[str], List[str]] = lambda string: string.split()
 
class Lexicon:
    rules: List[Rule]

    def __init__(self, rules: Sequence[Rule] | None = None) -> None:
        self.rules = list(rules) if rules else []

@dataclass(frozen=True)
class Lexeme:
    lemma: str
    words: List[str]

class Lexer:    
    def __init__(self, lexicon: Lexicon) -> None:
        self.lexicon = lexicon

    def analyze(self, chunk: str) -> Generator[Lexeme, None, None]:
        yield Lexeme('TEXT', words=[chunk])