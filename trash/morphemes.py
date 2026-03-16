from typing import Literal
from enum import Enum, auto
 
class Position(Enum):
    PREFIX = auto()   
    POSTFIX = auto()   
    INFIX = auto()       
    CIRCUMFIX = auto() 
    STANDALONE = auto() 

class Allomorph:
    def __init__(self, pattern: str, position: Position) -> None:
        self.pattern = pattern  
        self.position = position

    def is_valid(self, context: list) -> bool: 
        if self.position == Position.POSTFIX: 
            return len(context) > 0 and context[-1].type == "TEXT"
        return True
 
class Morpheme: 

    def __init__(self, sema: str, category: Literal['FREE', 'BOUND']) -> None:
        self.sema = sema  
        self.type = category 
        self.allomorphs = []

    def push(self, pattern: str, position: Position): 
        self.allomorphs.append(Allomorph(pattern, position))

    def __repr__(self):
        return f"<Morpheme: {self.sema} ({self.type})>"


h1 = Morpheme("LEVEL 1 HEADER", 'BOUND') 
h1.push(pattern=r"^#\s", position=Position.PREFIX) 
h1.push(pattern=r"^={3,}$", position=Position.POSTFIX)
 
bold = Morpheme("STRONG_EMPHASIS", 'BOUND') 
bold.push(pattern=r"\*\*", position=Position.CIRCUMFIX) 

math_block = Morpheme("MATHEMATICAL_EXPRESSION", 'BOUND')
math_block.push(pattern=r"\$\$", position=Position.CIRCUMFIX)
 
hr = Morpheme("HORIZONTAL_RULE", 'FREE')
hr.push(pattern=r"^-{3,}$", position=Position.STANDALONE)