from luthor.lexicon import Lexicon, Rule, Terminal

class Markdown:
    """
    Lexicon with full words and explicit context assignments.
    """
    lexicon = Lexicon([ 
            Rule(Terminal("<|HEADER|>", "#"),   pattern=r"^#(?=\s)"),
            Rule(Terminal("<|HEADER|>", "##"),  pattern=r"^##(?=\s)"),
            Rule(Terminal("<|HEADER|>", "###"), pattern=r"^###(?=\s)"),
             
            Rule(Terminal("<|HYPHEN|>", "-"),  pattern=r"^\s*-(?=\s)"),
             
            Rule(Terminal("<|FENCE|>", "```"), pattern=r"[`]{3}", content="<|CODE|>"),
            Rule(Terminal("<|FENCE|>", "`"),   pattern=r"`",      content="<|CODE|>"),
            
            Rule(Terminal("<|SIGN|>", "$$"), pattern=r"\$\$",     content="<|MATH|>"),
            Rule(Terminal("<|SIGN|>", "$"),  pattern=r"\$(?!\$)", content="<|MATH|>"),
             
            Rule(Terminal("<|STAR|>", "**"), pattern=r"\*\*"),    
            Rule(Terminal("<|STAR|>", "*"),  pattern=r"\*(?!\*)"),
               
            Rule(Terminal("<|MARK|>",   "!"), pattern=r"!"),
            Rule(Terminal("<|BRAKET|>", "["), pattern=r"\["),
            Rule(Terminal("<|BRAKET|>", "]"), pattern=r"\]"),
            Rule(Terminal("<|PARENTHESIS|>", "("), pattern=r"\("), 
            Rule(Terminal("<|PARENTHESIS|>", ")"), pattern=r"\)"), 
             
            Rule(Terminal("<|BAR|>", "|"),    pattern=r"\|"),
            Rule(Terminal("<|LINE|>", "---"), pattern=r"[-]{3,}"),
            Rule(Terminal("<|COLON|>", ":"),  pattern=r":"),
            Rule(Terminal("<|BREAK|>", "\n"), pattern=r"\n"),
        ]
    )