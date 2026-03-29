from pytest import fixture

@fixture
def markdown() -> str:
    return r"""# PyLuthor

![Figure](../assets/logo.png)
> [Figure 1:](figure:logo) This is a caption for a figure.

Figure [1](figure:logo) shows something, and this is a cite [Eric H, 2026](@eric2026latex).

This is a `code` block:

```python
def function(x,y,z):
    return y*z + x**2
```

Labeled math is accepted:

$$
E = mc^2
\tag{22}%(equation:einstein)
$$

Where equation [22](equation:einstein) is just:

$$
E = \sqrt{p^2 c^2 + m^2c^4},
$$

with $p = 0$. Here is a table:

| Header 1   | Header 2   |
| --------   | ---------- |
| Cell $x=1$ | Cell *a*   |
| Cell $x=2$ | Cell **b** |
> [Table 1](table:results) this is a caption with $LaTeX$.
 
This is a reference of table [1](table:results).
"""

@fixture
def latex() -> str:
    return r"""\section{PyLuthor}\label{pyluthor}

\begin{figure}
\centering
\includegraphics{../assets/logo.png}
\caption{This is a caption for a figure. \label{figure:logo}}
\end{figure}

Figure \ref{figure:logo} shows something, and this is a cite
\cite{eric2026latex}.

This is a \texttt{code} block:

\begin{verbatim}
def function(x,y,z):
    return y*z + x**2
\end{verbatim}

Labeled math is accepted:

\begin{equation}
E = mc^2
\label{equation:einstein}
\end{equation}

Where equation \ref{equation:einstein} is just:

\[
E = \sqrt{p^2 c^2 + m^2c^4},
\]

with \(p = 0\). Here is a table:

\begin{longtable}[]{@{}ll@{}}
\caption{this is a caption with \(LaTeX\).
\label{table:results}}\tabularnewline
\toprule\noalign{}
Header 1 & Header 2 \\
\midrule\noalign{}
\endfirsthead
\toprule\noalign{}
Header 1 & Header 2 \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
Cell \(x=1\) & Cell \emph{a} \\
Cell \(x=2\) & Cell \textbf{b} \\
\end{longtable}

This is a reference of table \ref{table:results}.
"""