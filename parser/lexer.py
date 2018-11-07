import ply.lex as lex
from ply.lex import TOKEN
import re

#s = '''CREATE TABLE test(int field, char field1)'''

tokens = (

	'CREATE', 'SHOW','TABLE','NAME', 'RPAREN', 'LPAREN', 'COMMA','VAR', 'int', 'char'

)
	
ident = r'[a-zA-Z_][a-zA-Z0-9_]\w*'

t_CREATE = r'CREATE'
t_TABLE = r'TABLE'
t_RPAREN = r'\)'
t_LPAREN = r'\('
t_COMMA = r','


@TOKEN(ident)
def t_NAME(t):

    if (t.value.upper() == 'CREATE'):
        t.type = 'CREATE'

    if (t.value.upper() == 'TABLE'):
        t.type = 'TABLE'
  
    if (t.value.lower() == 'int'):
        t.type = 'int'

    if (t.value.lower() == 'char'):
        t.type = 'char'
        
    return t



def t_error(t):
    print ("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
t_ignore = " "

lexer = lex.lex(reflags=re.UNICODE | re.DOTALL)

if __name__=="__main__":
    s = '''CREATE TABLE test(int field, char field1)'''

    lexer.input(s)

    while True:
        tok = lexer.token() # читаем следующий токен
        if not tok: break      # закончились печеньки
        print (tok)
