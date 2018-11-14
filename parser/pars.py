from lexer import tokens
import ply.yacc as yacc

class Node:

    def parts_str(self):
        st = []
        for part in self.parts:
            st.append( str( part ) )
        return "\n".join(st)

    def __repr__(self):
        return self.type + ":\n\t" + self.parts_str().replace("\n", "\n\t")

    def add_parts(self, parts):
        self.parts += parts
        return self

    def __init__(self, types, parts):
        self.type = types
        self.parts = parts

def p_start(p):
    '''start : create
             | show'''

    p[0] = p[1]

def p_create(p):
    '''create : CREATE create_body'''

    p[1] = Node(p[1], [])
    p[0] = p[1].add_parts([p[2]]) 

def p_show(p):
    '''show : SHOW CREATE TABLE NAME'''

    p[1] = Node(p[1], [])
    p[3] = Node(p[3], [])

    p[3] = p[3].add_parts([p[4]])
    p[0] = p[1].add_parts([p[3]])

     

def p_create_body(p):
    '''create_body : TABLE NAME LPAREN values RPAREN'''

    p[0] = Node(p[1], [])
    p[0] = p[0].add_parts([p[2]])
    p[0] = p[0].add_parts([p[4]])


def p_values(p):
    '''values : var 
              | values COMMA var'''
    if len(p) == 1:
        p[0] = Node('vars', [])
    elif len(p) == 2:
        p[0] = Node('vars', [p[1]])
    else:
        p[0] = p[1].add_parts([p[3]])

def p_var(p):
    '''var : NAME type'''
    p[0] = Node('var', [])
    p[0] = p[0].add_parts([p[1]])
    p[0] = p[0].add_parts([p[2]])

def p_type(p):
    '''type : int 
            | str
            | bol'''    
    p[0] = p[1]   

parser = yacc.yacc()

def build_tree(code):
    return parser.parse(code)