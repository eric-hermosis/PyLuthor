from luthor.latex import Document, Command, Geometry, Include, Bibliography
from luthor.latex.compiler import Compiler

if __name__ == '__main__':
    
    document = Document(
        preamble=[
            Command("documentclass", ["article"], options="12pt"),
            Command("usepackage", ["babel"], options="spanish,provide=*"),
            Command("usepackage", ["inputenc"], options="utf8"),
            Command("usepackage", ["fontenc"], options="T1"),
            Command("usepackage", ["lmodern"]),
            Command("usepackage", ["amsmath"]),
            Command("usepackage", ["amssymb"]),
            Command("usepackage", ["hyperref"]),
            Command("usepackage", ["cite"]),
            Command("usepackage", ["graphicx"]),
            Command("usepackage", ["caption"], options="font=small,labelfont=bf,margin=0.5cm"),
            Command("usepackage", ["geometry"]),
            Geometry(
                paper="a4paper",
                top="3.5cm",
                bottom="3.5cm",
                left="3.5cm",
                right="3.5cm"
            ),
            Command("setlength", ["\\parindent", "0pt"]),
            Command("setlength", ["\\parskip", "1em"]),
            Command("title", ["Markdown Example"]),
            Command("author", ["Eric Hermosis"]),
            Command("date", ["\\today"]),
        ],

        body=[
            Include('example/index'),
            Bibliography('example/references'),
            Include('example/appendix')
        ]
    ) 
    
    compiler = Compiler('article.tex')
    compiler.compile(document)