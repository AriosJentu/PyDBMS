import ply.lex as lex
from ply.lex import TOKEN
import re

#s = '''CREATE TABLE test(int field, char field1)'''

tokens = (

	'CREATE', 'SHOW', 'SELECT', 'FROM','TABLE','NAME', 'RPAREN', 'LPAREN', 'COMMA','VAR', 'int', 'str', 'bol'

)
	
ident = r'[a-zA-Z_][a-zA-Z0-9_]\w*'

t_CREATE = r'CREATE'
t_SHOW = r'SHOW'
t_SELECT = r'SELECT'

t_TABLE = r'TABLE'
t_FROM = r'FROM'

t_RPAREN = r'\)'
t_LPAREN = r'\('
t_COMMA = r','


@TOKEN(ident)
def t_NAME(t):

    if (t.value.upper() == 'CREATE'):
        t.type = 'CREATE'

    if(t.value.upper() == 'SHOW'):
        t.type = 'SHOW'

    if(t.value.upper() == 'SELECT'):
        t.type = 'SELECT'

    if (t.value.upper() == 'TABLE'):
        t.type = 'TABLE'
  
    if (t.value.upper() == 'FROM'):
        t.type = 'FROM'

    if (t.value.lower() == 'int'):
        t.type = 'int'

    if (t.value.lower() == 'bol'):
        t.type = 'bol'

    if (t.value.lower() == 'str'):
        t.type = 'str'    
        
    return t



def t_error(t):
    print ("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

t_ignore = ''' ' " '''

lexer = lex.lex(reflags=re.UNICODE | re.DOTALL)

if __name__=="__main__":
    s = '''CREATE TABLE test(int field, char field1)'''

    lexer.input(s)

    while True:
        tok = lexer.token() # читаем следующий токен
        if not tok: break      # закончились печеньки
        print (tok)
