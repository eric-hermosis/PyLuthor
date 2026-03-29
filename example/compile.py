from logging import basicConfig, INFO
from luthor.latex.document import Document, Command  
from luthor.compiler import Compiler
  
if __name__ == '__main__':  

    basicConfig(
        level=INFO, 
        format="[%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    document = Document(
        preamble=[  
            Command("documentclass", ["12pt"], {"article"}),
            Command("usepackage", ["spanish","provide=*"], {"babel"}),
            Command("usepackage", ["utf8"], {"inputenc"}),
            Command("usepackage", ["T1"], {"fontenc"}),
            Command("usepackage", {"lmodern"}),
            Command("usepackage", {"amsmath"}),
            Command("usepackage", {"amssymb"}),
            Command("usepackage", {"hyperref"}),
            Command("usepackage", {"cite"}),
            Command("usepackage", {"graphicx"}), 
            Command("usepackage", {"longtable"}),
            Command("usepackage", {"booktabs"}), 
            Command("usepackage", ["font=small","labelfont=bf","margin=0.5cm"], {"caption"}),
            Command("usepackage", ["paper=a4paper", "top=3.5cm", "bottom=3.5cm", "left=3.5cm", "right=3.5cm"], {"geometry"}), 
            Command("setlength", {"\\parindent"}, {"0pt"}),
            Command("setlength", {"\\parskip"}, {"1em"}),
            Command("title", {"Markdown Example"}),
            Command("author", {"Eric Hermosis"}),
            Command("date", {"\\today"}),  
        ], 

        body=[
            Command("maketitle"),  
            Command("include", {"chapter/index"}),
            Command("bibliographystyle", {"plain"}), 
            Command("bibliography", {"references"}) 
        ]
    ) 
 
    compiler = Compiler(filename="output.pdf", builddir="build") 
    compiler.compile(document)