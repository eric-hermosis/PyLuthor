from typing import Sequence
from typing import List 
from luthor.scanner import Token
 
class Production:
    head: str
    body: list[str]

    def __init__(self, head: str, body: Sequence[str]) -> None:
        self.head = head
        self.body = list(body)
        self.indices = [index for index, symbol in enumerate(self.body) if symbol == 'BODY']
        self.parts = self.split()

    def split(self) -> list[tuple[str, ...]]:
        parts = []
        start = 0
        for position in self.indices:
            parts.append(tuple(self.body[start:position]))
            start = position + 1
        parts.append(tuple(self.body[start:]))
        return parts

    @property
    def recursive(self) -> bool:
        return bool(self.indices)

    @property
    def order(self) -> int:
        return len(self.indices)

    @property
    def opener(self) -> tuple[str, ...]:
        return self.parts[0]

    @property
    def closer(self) -> tuple[str, ...]:
        return self.parts[-1] if self.recursive else tuple()

    def opens(self, tokens: Sequence[Token]) -> bool:
        if not self.recursive or len(tokens) < len(self.opener):
            return False
        return all(tokens[index].name == self.opener[index] for index in range(len(self.opener)))

    def closes(self, tokens: Sequence[Token]) -> bool:
        if not self.recursive or len(tokens) < len(self.closer):
            return False
        return all(tokens[index].name == self.closer[index] for index in range(len(self.closer)))

    def matches(self, tokens: Sequence[Token]) -> bool:
        if self.recursive or len(tokens) < len(self.body):
            return False
        return all(tokens[index].name == self.body[index] for index in range(len(self.body))) 

class Boundary:
    sequence: List[str]

    def __init__(self, sequence: Sequence[str]) -> None:
        self.sequence = list(sequence)

    def matches(self, tokens: Sequence[Token]) -> bool:
        if len(tokens) < len(self.sequence):
            return False
        return all(tokens[index].name == self.sequence[index] for index in range(len(self.sequence)))

class Grammar : 
    recursions : List[Production]
    imperations: List[Production]

    def __init__(self, productions: Sequence[Production]) -> None:

        self.recursions = sorted(
            [production for production in productions if production.recursive],
            key=lambda production: len(production.opener),
            reverse=True,
        )

        self.imperations = sorted(
            [production for production in productions if not production.recursive],
            key=lambda production: len(production.body),
            reverse=True,
        )