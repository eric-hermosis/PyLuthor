from __future__ import annotations

class Node:
    type: str 
    children: list[Node]

    def __init__(self, type: str) -> None:
        self.type = type
        self.children = []

    def link(self, node: Node) -> None:
        self.children.append(node) 