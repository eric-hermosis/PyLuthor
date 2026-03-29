from typing import List, Sequence
from re import Match, Pattern, compile 

class Symbol:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Symbol):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False
    
    def __hash__(self) -> int:
        return hash(self.name) 


class Terminal(Symbol): 
    def __init__(self, name: str, context: str | None = None) -> None:
        super().__init__(name)
        self.context = context

    def __repr__(self) -> str: 
        return f"Terminal({self.name})"


class Nonterminal(Symbol):
    pass


class Rule:
    terminal: Terminal
    pattern : Pattern[str]
    content : str | None

    def __init__(self, terminal: Terminal | str, pattern: str | Pattern[str], content: str | None = None) -> None:
        self.terminal = terminal if isinstance(terminal, Terminal) else Terminal(terminal)
        if not isinstance(self.terminal, Terminal):
            raise TypeError(f"expected 'terminal' to be Terminal or str, got {type(terminal).__name__}")
        
        self.pattern = compile(pattern) if isinstance(pattern, str) else pattern
        if not isinstance(self.pattern, Pattern):
            raise TypeError(f"expected 'pattern' to be regex Pattern or str, got {type(pattern).__name__}")
        
        self.content = content 

    def match(self, chunk: str, position: int) -> Match[str] | None:
        return self.pattern.match(chunk, position) 

class Lexicon:
    rules: List[Rule]

    def __init__(self, rules: Sequence[Rule]) -> None:
        self.rules = list(rules)

