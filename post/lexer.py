import ply.lex as lex

tokens = (
    'NUMBER',
    'DICE',
    'DICE_CONDITION',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'EQ',
    'NE',
    'LT',
    'LE',
    'GT',
    'GE'
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_EQ = r'=='
t_NE = r'!='
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='

def t_DICE_CONDITION(t):
    r'\d+[bB]\d+>=\d+'
    t.value = t.value.lower()
    return t

def t_DICE(t):
    r'\d+[dDbB]\d+'
    t.value = t.value.lower()
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()
