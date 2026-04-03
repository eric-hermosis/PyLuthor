from luthor.latex.document import Document, Command  
from luthor.compiler import Compiler

document = Document(
    preamble=[  
        Command("documentclass", ["12pt"], {"article"}),
        Command("usepackage", ["spanish"], {"babel"}),
        Command("title", {"Markdown Example"}),
        Command("author", {"Eric Hermosis"}),
    ], 
    body=[
        Command("maketitle"),  
        Command("include", {"README"}), #  wherever your .md files are.
        Command("bibliography", {"references"}) 
    ]
) 

latex = '\n'.join([str(command) for command in document.forward()])
print(latex)