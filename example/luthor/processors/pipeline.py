from typing import List
from typing import Sequence
from luthor.processors.abstract import Processor

class Pipeline(Processor): 
    processors: List[Processor]

    def __init__(self, processors: Sequence[Processor]):
        self.processors = list(processors)

    def process(self, text: str) -> str:
        for processor in self.processors:
            text = processor.process(text)
        return text   