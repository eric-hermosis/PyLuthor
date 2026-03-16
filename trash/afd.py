
LEXICON_RULES = {
    "initial_state": "START",
    "states": {
        "START": {
            "#": "HEADER_HASH",
            "default": "TEXT"
        },
        "HEADER_HASH": {
            "#": "HEADER_HASH",
            " ": "HEADER_CONTENT",
            "default": "TEXT"
        },
        "HEADER_CONTENT": {
            "\n": "ACCEPT_HEADER",
            "default": "HEADER_CONTENT"
        },
        "TEXT": {
            "\n": "ACCEPT_TEXT",
            "default": "TEXT"
        }
    },
    "accepting_states": ["ACCEPT_HEADER", "ACCEPT_TEXT"]
}

class DFADriver:
    def __init__(self, config):
        self.rules = config["states"]
        self.start_state = config["initial_state"]
        self.accepting = config["accepting_states"]

    def tokenize(self, code):
        current_state = self.start_state
        lexeme = ""
        
        for char in code: 
            transitions = self.rules.get(current_state, {})
            next_state = transitions.get(char, transitions.get("default", "ERROR"))
            
            if next_state == "ERROR":
                raise SyntaxError(f"Lexema inválido en estado {current_state}")
            
            lexeme += char
            current_state = next_state
             
            if current_state in self.accepting:
                print(f"TOKEN ENCONTRADO: [{current_state}] -> '{lexeme.strip()}'") 
                current_state = self.start_state
                lexeme = ""
 
lexer = DFADriver(LEXICON_RULES)
lexer.tokenize("### Titulo\nEste es un texto\n")