from luthor.latex.document import Document, Command  

def test_commands():
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
    assert latex == r"""\documentclass[12pt]{article}
\usepackage[spanish]{babel}
\title{Markdown Example}
\author{Eric Hermosis}
\begin{document}
\maketitle
\include{README}
\bibliography{references}
\end{document}"""

def test_implicit_commands():
    document = Document([  
        ("documentclass", ["12pt"], {"article"}),
        ("usepackage", ["spanish"], {"babel"}),
        ("title", {"Markdown Example"}),
        ("author", {"Eric Hermosis"}),
    ], [
        ("maketitle"),  
        ("include", {"README"}), 
        ("bibliography", {"references"}) 
    ]
    ) 

    latex = '\n'.join([str(command) for command in document.forward()])
    assert latex == r"""\documentclass[12pt]{article}
\usepackage[spanish]{babel}
\title{Markdown Example}
\author{Eric Hermosis}
\begin{document}
\maketitle
\include{README}
\bibliography{references}
\end{document}""" 