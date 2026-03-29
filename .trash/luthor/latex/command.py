from __future__ import annotations
from typing import Sequence
from typing import Generator, List, Set

class Command:
    name: str 
    arguments: List[Set[str] | Sequence[str]]

    def __init__(self, name: str, *arguments: Set[str] | Sequence[str]) -> None:
        self.name = name
        self.arguments = []

        for index, argument in enumerate(arguments):
            if isinstance(argument, set):
                assert len(argument) == 1
                self.arguments.append(argument)

            elif isinstance(argument, (list, tuple)):
                self.arguments.append(argument)
            else:
                raise TypeError(
                    f"Argument {index} must be a Set[str] (target), List[str] (optional) or Tuple[str] (required), "
                    f"got {type(argument)}"
                )

    def __repr__(self) -> str: 
        strings = [repr(self.name)] + [repr(argument) for argument in self.arguments]
        return f"Command({', '.join(strings)})"

    def __str__(self) -> str:
        string = f"\\{self.name}"  
        for argument in self.arguments:
            content = ','.join(argument)
            if isinstance(argument, (set, tuple)): 
                string += f"{{{content}}}"
            else: 
                string += f"[{content}]" 
        return string

    def forward(self) -> Generator[Command, None, None]:
        yield self