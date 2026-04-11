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
            ("documentclass", ["12pt"], {"article"}),
            ("usepackage", ["spanish","provide=*"], {"babel"}),
            ("usepackage", ["utf8"], {"inputenc"}),
            ("usepackage", ["T1"], {"fontenc"}),
            ("usepackage", {"lmodern"}),
            ("usepackage", {"amsmath"}),
            ("usepackage", {"amssymb"}),
            ("usepackage", {"hyperref"}),
            ("usepackage", {"cite"}),
            ("usepackage", {"graphicx"}), 
            ("usepackage", {"longtable"}),
            ("usepackage", {"booktabs"}), 
            ("usepackage", ["font=small","labelfont=bf","margin=0.5cm"], {"caption"}),
            ("usepackage", ["paper=a4paper", "top=3.5cm", "bottom=3.5cm", "left=3.5cm", "right=3.5cm"], {"geometry"}), 
            ("setlength", {"\\parindent"}, {"0pt"}),
            ("setlength", {"\\parskip"}, {"1em"}),
            ("title", {"Markdown Example"}),
            ("author", {"Eric Hermosis"}),
            ("date", {"\\today"}),  
        ], 

        body=[
            ("maketitle"),  
            ("include", {"chapter/index"}),
            ("bibliographystyle", {"plain"}), 
            ("bibliography", {"references"}) 
        ]
    ) 
 
    compiler = Compiler(filename="output.pdf", builddir="build") 
    compiler.transpile(document)