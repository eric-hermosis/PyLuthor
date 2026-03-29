from subprocess import CalledProcessError
from subprocess import run

from luthor.processors.abstract import Processor 

class Pandoc(Processor): 

    def __init__(self, source: str = 'markdown', target: str = 'latex') -> None: 
        self.source = source
        self.target = target 

    def process(self, text: str) -> str:
        try:
            result = run(
                ['pandoc', '-f', self.source, '-t', self.target],
                input=text,
                text=True,
                capture_output=True,
                check=True
            )
            return result.stdout
        except CalledProcessError as exception:
            return f"% Pandoc error: {exception.stderr}"
        
        except FileNotFoundError:
            return "% Error: Pandoc is not installed."  