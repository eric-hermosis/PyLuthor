from luthor.lexing import Lexicon, Rule
from luthor.parser import Grammar, Production

class Markdown:

    lexicon = Lexicon([

        Rule('ENDL', r'(\n)', '\n'),

        Rule('H4', r'(^####)(?:\s*)(.*?)(\n|$)', '####'),
        Rule('H3', r'(^###)(?:\s*)(.*?)(\n|$)', '###'),
        Rule('H2', r'(^##)(?:\s)(.*?)(\n|$)', '##'),
        Rule('H1', r'(^#)(?:\s)(.*?)(\n|$)', '#'),
        Rule('LINK', r'(\[)(.*?)(\]\()(.*?)(\))', '['),
        Rule('ITEM', r'(^[-\*])(?:\s+)(.*?)(\n|$)', '-'),

        Rule('ROW_START', r'(^\|)', '|'),
        Rule('ROW_END', r'(\|)(?=\s*\n|$)', '|'),
        Rule('PIPE', r'(\|)', '|'),
    
        Rule('FIG_OPEN', r'(\!\[)', '!['),
        Rule('FIG_SEP', r'(\]\()', ']('),
        Rule('CLOSE_PAREN', r'(\))', ')'),

        Rule('STAR', r'(\*\*)(.*?)(\*\*)(?!\*)', '**'),
        Rule('STAR', r'(\*)(.*?)(\*)', '*'),
        Rule('SIGN', r'(\$\$)', '$$', 'MATH'),
        Rule('SIGN', r'(\$)(.*?)(\$)', '$', 'MATH'),
        Rule('TICK', r'(\```)', '```', 'CODE'),
        Rule('TICK', r'(\`)', '`', 'CODE'),
    ]) 
    
    grammar = Grammar( 

        productions=[   
            Production('Title',        ['H1', '#',   'ENDL', '\n']),
            Production('Link', ['LINK', '[', 'CLOSE_PAREN', ')']),
            Production('Section',      ['H2', '##',  'ENDL', '\n']),
            Production('Subsection',   ['H3', '###', 'ENDL', '\n']), 
            Production('Item',         ['ITEM', '-', 'ENDL', '\n']),
            Production('TableRow',     ['ROW_START', '|', 'ROW_END', '|']),
            Production('Figure',       ['FIG_OPEN', '![', 'CLOSE_PAREN', ')']),
                        
            Production('Bold',         ['STAR', '**']),
            Production('Italic',       ['STAR', '*']),
            Production('Math[Block]',  ['SIGN', '$$']), 
            Production('Math[Inline]', ['SIGN', '$']), 
            Production('Code[Block]',  ['TICK', '```']),
            Production('Code[Inline]', ['TICK', '`']),
        ],
        
        content={
            'TEXT': 'Text',
            'ITEM': 'Item',
            'MATH': 'Math[Content]',
            'CODE': 'Code[Content]',
            'ENDL': 'Break',
            'FIG_SEP': 'UrlSeparator',  
            'CLOSE_PAREN': 'Text',
            'PIPE': 'ColumnSeparator',
        }
    )