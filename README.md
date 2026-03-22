# PyLuthor


  Break('\n')
  Section
    Text('Section')
  Break('\n')
  Text('Inline math like ')
  Math[Inline]
    Math[Content]('f(x) = x**2')
  Text(' and math blocks:')
  Break('\n')
  Break('\n')
  Math[Block]
    Math[Content]('\nf(x,y,z) = x*y + y*z + z*x,\n')
  Break('\n')
  Break('\n')
  Text('where:')
  Break('\n')
  Item
    Math[Inline]
      Math[Content]('f')
    Text(' is a ')
    Bold
      Text('function')
    Text(',')
  Item
    Text('and ')
    Math[Inline]
      Math[Content]('x')
    Text(', ')
    Math[Inline]
      Math[Content]('y')
    Text(', ')
    Math[Inline]
      Math[Content]('z')
    Text(' are variables.')
  Break('\n')
  Subsection
    Text('Subsection here')
  Break('\n')
  Text('Inline ')
  Code[Inline]
    Code[Content]('code')
  Text(' and code blocks:')
  Break('\n')
  Break('\n')
  Code[Block]
    Code[Content]('\ndef square(x):\n    return x**2\n')
  Break('\n')
  Break('\n')
  Text('This is an example with ')
  Bold
    Text('bold and ')
    Italic
      Text('italic')
  Text(' emphasis. ')
  Break('\n')
  Break('\n')
  TableRow
    Text(' Header 1 ')
    ColumnSeparator('|')
    Text(' Header 2   ')
  Break('\n')
  TableRow
    Text(' -------- ')
    ColumnSeparator('|')
    Text(' ---------- ')
  Break('\n')
  TableRow
    Text(' Cell ')
    Math[Inline]
      Math[Content]('1')
    ColumnSeparator('|')
    Text(' Cell ')
    Bold
      Text('2')
  Break('\n')
  Break('\n')
  Text('Here is an image for the document:')
  Break('\n')
  Figure
    Text('A cool landscape')
    UrlSeparator('](')
    Text('https://example.com/image.png')
  Break('\n')
  Break('\n')

\section{Title}

\section{Section}

Inline math like $f(x) = x**2$ and math blocks:

\begin{equation}
f(x,y,z) = x*y + y*z + z*x,
\end{equation}


where:
\item $f$ is a \textbf{function},
\item and $x$, $y$, $z$ are variables.

\subsection{Subsection here}

Inline \texttt{code} and code blocks:

\begin{verbatim}
def square(x):
    return x**2
\end{verbatim}


This is an example with \textbf{bold and \textit{italic}} emphasis. 

Header 1 & Header 2 \\
-------- & ---------- \\
Cell & $1$ & Cell & \textbf{2} \\

Here is an image for the document:
\begin{figure}[h]
\centering
\includegraphics{https://example.com/image.png}
\caption{A cool landscape}
\end{figure}



(pyluthor-py3.13) eric-hermosis@ideapad:~/Repositorios/PyLuthor$ python main.py 
Document
  Break('\n')
  Title
    Text('Title')
  Break('\n')
  Section
    Text('Section')
  Break('\n')
  Text('Inline math like ')
  Math[Inline]
    Math[Content]('f(x) = x**2')
  Text(' and math blocks:')
  Break('\n')
  Break('\n')
  Math[Block]
    Math[Content]('\nf(x,y,z) = x*y + y*z + z*x,\n')
  Break('\n')
  Break('\n')
  Text('where:')
  Break('\n')
  Item
    Math[Inline]
      Math[Content]('f')
    Text(' is a ')
    Bold
      Text('function')
    Text(',')
  Item
    Text('and ')
    Math[Inline]
      Math[Content]('x')
    Text(', ')
    Math[Inline]
      Math[Content]('y')
    Text(', ')
    Math[Inline]
      Math[Content]('z')
    Text(' are variables.')
  Break('\n')
  Subsection
    Text('Subsection here')
  Break('\n')
  Text('Inline ')
  Code[Inline]
    Code[Content]('code')
  Text(' and code blocks:')
  Break('\n')
  Break('\n')
  Code[Block]
    Code[Content]('\ndef square(x):\n    return x**2\n')
  Break('\n')
  Break('\n')
  Text('This is an example with ')
  Bold
    Text('bold and ')
    Italic
      Text('italic')
  Text(' emphasis. ')
  Break('\n')
  Break('\n')
  TableRow
    Text(' Header 1 ')
    ColumnSeparator('|')
    Text(' Header 2   ')
  Break('\n')
  TableRow
    Text(' -------- ')
    ColumnSeparator('|')
    Text(' ---------- ')
  Break('\n')
  TableRow
    Text(' Cell ')
    Math[Inline]
      Math[Content]('1')
    ColumnSeparator('|')
    Text(' Cell ')
    Bold
      Text('2')
  Break('\n')
  Break('\n')
  Text('Here is an image for the document:')
  Break('\n')
  Figure
    Text('A cool landscape')
    UrlSeparator('](')
    Text('https://example.com/image.png')
  Break('\n')
  Break('\n')

\section{Title}

\section{Section}

Inline math like $f(x) = x**2$ and math blocks:

\begin{equation}
f(x,y,z) = x*y + y*z + z*x,

\end{equation}


where:
\item $f$ is a \textbf{function},
\item and $x$, $y$, $z$ are variables.

\subsection{Subsection here}

Inline \texttt{code} and code blocks:

\begin{verbatim}
def square(x):
    return x**2
\end{verbatim}


This is an example with \textbf{bold and \textit{italic}} emphasis. 

Header 1 & Header 2 \\
-------- & ---------- \\
Cell & $1$ & Cell & \textbf{2} \\

Here is an image for the document:
\begin{figure}[h]
\centering
\includegraphics{https://example.com/image.png}
\caption{A cool landscape}

\end{figure}