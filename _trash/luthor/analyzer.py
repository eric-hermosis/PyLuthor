
from luthor.parser import Node

class Analyzer: 

    def __init__(self, root: Node):
        self.root = root

    def analyze(self) -> Node:
        self._collapse_tables(self.root)
        self._attach_metadata(self.root)
        return self.root
 
    def _collapse_tables(self, parent: Node) -> None: 
        new_children: list[Node] = []
        buffer: list[Node] = []
        break_buffer: list[Node] = []

        def flush_buffer():
            if buffer:
                table_node = Node("Table")
                for row in buffer:
                    table_node.link(row)
                new_children.extend(break_buffer)
                new_children.append(table_node)
                buffer.clear()
                break_buffer.clear()
            elif break_buffer:
                new_children.extend(break_buffer)
                break_buffer.clear()

        for child in parent.children:
            self._collapse_tables(child)

            if child.kind == "TableRow":
                buffer.append(child)
            elif child.kind == "Break":
                break_buffer.append(child)
            else:
                flush_buffer()
                new_children.append(child)

        flush_buffer()
        parent.children = new_children
        
    def _attach_metadata(self, parent: Node) -> None:
        import re

        meta_re = re.compile(
            r'(?s)^(?P<prefix>.*?)<!--(?P<kind>table|figure):(?P<label>.+?)-->(?P<suffix>.*)$'
        )

        def previous_non_break(nodes: list[Node]) -> Node | None:
            j = len(nodes) - 1
            while j >= 0 and nodes[j].kind == "Break":
                j -= 1
            return nodes[j] if j >= 0 else None

        new_children: list[Node] = []
        i = 0

        while i < len(parent.children):
            node = parent.children[i]
            self._attach_metadata(node)

            if node.kind == "Text" and node.value:
                m = meta_re.match(node.value)
                if m:
                    prefix = m.group("prefix")
                    kind = m.group("kind")
                    label = m.group("label").strip()
                    suffix = m.group("suffix")

                    target = previous_non_break(new_children)

                    if target and (
                        (kind == "table" and target.kind == "Table") or
                        (kind == "figure" and target.kind == "Figure")
                    ):
                        target.value = label

                        caption_parts: list[str] = []
                        if prefix.strip():
                            caption_parts.append(prefix.strip())
                        if suffix.strip():
                            caption_parts.append(suffix.strip())

                        k = i + 1
                        while k < len(parent.children):
                            follower = parent.children[k]

                            if follower.kind == "Break":
                                k += 1
                                continue

                            if follower.kind == "Text" and follower.value and follower.value.strip():
                                caption_parts.append(follower.value.strip())
                                k += 1
                                continue

                            break

                        if caption_parts:
                            target.caption = " ".join(caption_parts)

                        i = k
                        continue

            new_children.append(node)
            i += 1

        parent.children = new_children