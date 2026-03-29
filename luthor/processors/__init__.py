from luthor.processors.abstract import Processor as Processor
from luthor.processors.pipeline import Pipeline
from luthor.processors.regex import Regex 

CUSTOM_MARKDOWN_TO_LATEX = Pipeline([
    Regex("Strip Code Tags", 
                r'(?m)^(```+)[ \t]*[a-zA-Z0-9_+-]+[ \t]*$', 
                r'\1'),
    Regex("Format Tables", 
                r'(\|[ \t]*\n)\[[^\]]+\]\((table:[^)]+)\)[ \t]*(.*)', 
                r'\1: \3 \\label{\2}'),
    Regex("Format Figures", 
                r'!\[.*?\]\((.*?)\)\s*\n\[[^\]]+\]\((figure:[^)]+)\)[ \t]*(.*)', 
                r'![\3 \\label{\2}](\1)'),
    Regex("Format Equations", 
                r'\$\$((?:(?!\$\$)[\s\S])*?)[ \t]*(?:\\tag\{[^}]*\})?[ \t]*%\((equation:[^)]+)\)((?:(?!\$\$)[\s\S])*?)\$\$', 
                r'\\begin{equation}\1\\label{\2}\3\\end{equation}'),
    Regex("Resolve Cross-references", 
                r'\[[^\]]+\]\(((?:table|figure|equation):[^)]+)\)', 
                r'\\ref{\1}'),
    Regex("Resolve Citations", 
                r'\[[^\]]+\]\(@([^)]+)\)', 
                r'\\cite{\1}')
])