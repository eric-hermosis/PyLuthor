from pytest import fixture
from luthor.latex import Document, Command, Geometry, Include, Bibliography

def test_document():
    
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
            Command("title", ["Inference Mechanics"]),
            Command("author", ["Eric Hermosis"]),
            Command("date", ["\\today"]),
        ]
    ) 

    result = r"""\documentclass[12pt]{article}
\usepackage[spanish,provide=*]{babel}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{hyperref}
\usepackage{cite}
\usepackage{graphicx}
\usepackage[font=small,labelfont=bf,margin=0.5cm]{caption}
\usepackage{geometry}
\geometry{a4paper,top=3.5cm,bottom=3.5cm,left=3.5cm,right=3.5cm}
\setlength{\parindent}{0pt}
\setlength{\parskip}{1em}
\title{Inference Mechanics}
\author{Eric Hermosis}
\date{\today}
\begin{document}
\maketitle

\end{document}"""
    assert result == document.to_latex()