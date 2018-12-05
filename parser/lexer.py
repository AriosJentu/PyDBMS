import ply.lex as lex
from ply.lex import TOKEN
import re
    
#s = '''CREATE TABLE test(int field, char field1)'''

tokens = (

	'CREATE', 'SHOW', 'SELECT', 'INSERT', 
    'FROM', 'INTO', 'TABLE', 'WHERE',
    'NAME', 'VALUES', 
    'RPAREN', 'LPAREN', 'COMMA', 
    'int', 'str', 'bol',
    'EQUAL', 'NOT_EQUAL', 'GREATER_THAN', 'LESS_THAN', 
    'GREATER_THAN_OR_EQUAL', 'LESS_THAN_OR_EQUAL', 'BETWEEN', 
    'LIKE', 'IN', 'OR', 'NOR', 'NOT', 'AND', 'NAND', 
    'PLUS', 'MINUS', 'MUL', 'TRUE_DIV', 'FLOOR_DIV','PERCENT', 'POWER'
)
	                       
ident = r'[a-z a-zA-Z0-9_ \- \+]\w*'

t_CREATE = r'CREATE'
t_SHOW = r'SHOW'
t_SELECT = r'SELECT'
t_INSERT = r'INSERT'

t_TABLE = r'TABLE'
t_FROM = r'FROM'
t_INTO = r'INTO'
t_WHERE = r'WHERE'

t_VALUES = r'VALUES'

t_RPAREN = r'\)'
t_LPAREN = r'\('
t_COMMA = r','

t_EQUAL = r'\=\=|\=|"IS"' 
t_NOT_EQUAL = r'\!=|\<>'
t_GREATER_THAN = r'\>'
t_LESS_THAN = '\<'
t_GREATER_THAN_OR_EQUAL = r'\>='
t_LESS_THAN_OR_EQUAL = r'\<='
t_BETWEEN = r'BETWEEN'
t_LIKE = r'LIKE'
t_IN = r'IN'
t_OR = 'OR'#+
t_NOR = 'NOR'#+
t_NOT = '\!|NOT'##
t_NAND = 'NAND'#+
t_AND = 'AND'#+
t_PLUS = '\+'##
t_MINUS = '\-'##
t_MUL = '\*'
t_TRUE_DIV = '\/' 
t_FLOOR_DIV = '\/\/'
t_PERCENT = '\%'
t_POWER = '\^|\*\*'##


@TOKEN(ident)
def t_NAME(t):


    if (t.value.upper() == 'CREATE'):
        t.type = 'CREATE'

    elif (t.value.upper() == 'SHOW'):
        t.type = 'SHOW'

    elif (t.value.upper() == 'SELECT'):
        t.type = 'SELECT'

    elif (t.value.upper() == 'INSERT'):
        t.type = 'INSERT'


    elif (t.value.upper() == 'TABLE'):
        t.type = 'TABLE'
  
    elif (t.value.upper() == 'FROM'):
        t.type = 'FROM'

    elif (t.value.upper() == 'INTO'):
        t.type = 'INTO'

    elif(t.value.upper() == 'WHERE'):
        t.type = 'WHERE'


    elif (t.value.upper() == 'VALUES'):
        t.type = 'VALUES'


    elif (
            t.value.lower() == 'int' or
            t.value.lower() == 'integer'
        ):
        t.type = 'int'

    elif (
            t.value.lower() == 'bol' or
            t.value.lower() == 'bool'
        ):
        t.type = 'bol'

    elif (
            t.value.lower() == 'str' or
            t.value.lower() == 'string'
        ):
        t.type = 'str'    
    

    elif (t.value.upper() == 'BETWEEN'):
        t.type = 'BETWEEN'

    elif (t.value.upper() == 'LIKE'):
        t.type = 'LIKE'

    elif (t.value.upper() == 'IN'):
        t.type = 'IN'

    elif (t.value.upper() == 'IS'):
        t.type = 'EQUAL'

    elif (t.value.upper() == 'OR'):
        t.type = 'OR'

    elif (t.value.upper() == 'NOR'):
        t.type = 'NOR'

    elif (t.value.upper() == 'NOT'):
        t.type = 'NOT'

    elif (t.value.upper() == 'NAND'):
        t.type = 'NAND'

    elif (t.value.upper() == 'AND'):
        t.type = 'AND'

    elif (t.value == '+'):
        t.type = 'PLUS'

    elif (t.value == '-'):
        t.type = 'MINUS'

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
