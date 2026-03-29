# PyLuthor

(pyluthor-py3.13) eric-hermosis@ideapad:~/Repositorios/PyLuthor$ python main3.py 
Root
  Title({'level': 1})
    Text('Section')
  Break('\n')
  Text('This is an example with ')
  Bold
    Text('bold')
  Text(' and ')
  Italic
    Text('italic')
  Text(' emphasis.')
  Break('\n')
  Break('\n')
  Section({'level': 2})
    Text('Subsection')
  Break('\n')
  Text('Inline math like ')
  Math[Inline]
    MathText('f(x) = x^2')
  Text(' and math blocks:')
  Break('\n')
  Break('\n')
  Math[Block]
    MathText('\nf(x,y,z) = xy + yz + zx,\n')
  Break('\n')
  Break('\n')
  Text('where:')
  Break('\n')
  List
    Item
      Math[Inline]
        MathText('f')
      Text(' is a ')
      Bold
        Text('function')
      Text(',')
    Item
      Text('and ')
      Math[Inline]
        MathText('x')
      Text(', ')
      Math[Inline]
        MathText('y')
      Text(', ')
      Math[Inline]
        MathText('z')
      Text(' are variables.')
  Break('\n')
  Subsection({'level': 3})
    Text('Subsubsection')
  Break('\n')
  Text('Inline ')
  Code[Inline]
    CodeText('code')
  Text(' and code blocks:')
  Break('\n')
  Break('\n')
  Code[Block]
    CodeText('\ndef square(x):\n\treturn x**2\n')
  Break('\n')
  Break('\n')
  Table({'caption': [Link({'label': 'Table 1:', 'target': 'table:example'}), Text(' This is the '), Italic
  Text('caption'), Text(' of the table where '), Math[Inline]
  MathText('x=1'), Text(' is math and '), Bold
  Text('b'), Text(' have emphasis.')], 'id': 'table:example'})
    TableRow
      RowStart('|')
      Text(' Header 1   ')
      ColumnSeparator('|')
      Text(' Header 2   ')
      RowEnd('|')
    TableRow
      RowStart('|')
      Text(' --------   ')
      ColumnSeparator('|')
      Text(' ---------- ')
      RowEnd('|')
    TableRow
      RowStart('|')
      Text(' Cell ')
      Math[Inline]
        MathText('x=1')
      ColumnSeparator('|')
      Text(' Cell ')
      Bold
        Text('b')
      RowEnd('|')
  Break('\n')
  Link({'label': 'Table 1:', 'target': 'table:example'})
  Text(' This is the ')
  Italic
    Text('caption')
  Text(' of the table where ')
  Math[Inline]
    MathText('x=1')
  Text(' is math and ')
  Bold
    Text('b')
  Text(' have emphasis.')
  Break('\n')
  Break('\n')
  Text('Here table ')
  Link({'label': '1', 'target': 'table:example'})
  Text(' is a table. An example of an image:')
  Break('\n')
  Break('\n')
  Figure({'alt': 'PyLuthor logo', 'src': 'logo.png', 'caption': [Link({'label': 'Figure 1:', 'target': 'figure:logo'}), Text(' This is the '), Italic
  Text('caption'), Text(' of the image.')], 'id': 'figure:logo'})
  Break('\n')
  Break('\n')
  Text('Can be referenced as figure ')
  Link({'label': '1', 'target': 'figure:logo'})
  Text(' just like with tables.')