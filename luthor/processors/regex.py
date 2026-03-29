from re import Pattern
from re import compile, sub
from luthor.processors.abstract import Processor

class Regex(Processor): 
    def __init__(self, name: str, pattern: str | Pattern[str], replacement: str):
        self.name = name
        self.pattern = pattern if isinstance(pattern, Pattern) else compile(pattern)
        self.replacement = replacement

    def process(self, text: str) -> str:
        return sub(self.pattern, self.replacement, text) 