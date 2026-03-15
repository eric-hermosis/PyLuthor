from enum import Enum, auto

class MorphemeType(Enum):
    FREE = auto()        
    BOUND = auto()       
    INFLECTIONAL = auto() 
    DERIVATIONAL = auto()

class Morpheme: 
    def __init__(self, sema: str, type: MorphemeType): 
        self.sema = sema  
        self.type = type 
        self.allomorphs = []

    def push(self, pattern: str, condition: str = "Any"):
        """
        Define cómo se manifiesta este morfema en el texto (Significante).
        """
        self.allomorphs.append({
            "representation": pattern,
            "condition": condition
        })

    def __repr__(self):
        return f"<Morpheme: {self.sema} ({self.type.name})>"
    

h1 = Morpheme("LEVEL 1 HEADER", MorphemeType.BOUND) 
h1.push(pattern=r"^#\s", condition="Line Start") 
h1.push(pattern=r"\n={3,}\n", condition="Underline Postfix")