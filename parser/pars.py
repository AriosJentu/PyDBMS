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

    def __init__(self, type, parts):
        self.type = type
        self.parts = parts


def p_start(p):
    '''start : CREATE body'''

    p[1] = Node(p[1], [])
    p[0] = p[1].add_parts([p[2]]) 



def p_body(p):
    '''body : NAME'''

    p[0] = p[1]


parser = yacc.yacc()

def build_tree(code):
    return parser.parse(code)