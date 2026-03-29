from abc import ABC, abstractmethod

class Processor(ABC):
    
    @abstractmethod
    def process(self, text: str) -> str:
        raise NotImplementedError("Subclasses must implement process()") 
