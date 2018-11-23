from lexer import tokens
import ply.yacc as yacc

class Struct:

    def __init__(self, **dictionary):
        self.__dict__.update(dictionary)

    def __getitem__(self, name):
        return self.__dict__[name]

    def __setitem__(self, name, value):
        self.__dict__[name] = value

    def __iter__(self):
        for i in self.__dict__.keys():
            yield i


class PCreate(Struct):

    def __init__(self, name=""):

        self.name = name
        self.values = PValues()
        self.types = PTypes()
        
    def set_name(self, name):
        self.name = name


    def set_vars(self, vars_):
        
        self.values = vars_.vars[0]
        self.types = vars_.vars[1]

class Vars:
    def __init__(self):
        self.vars = [[], []]

    def append_values(self, *values):

        self.vars[0].append(*values)
        

    def append_types(self, *types):

        self.vars[1].append(*types)
        

class PValues(Struct):

    def __init__(self, *values):
        self.values = [i for i in values]

    def append(self, *values):
        for i in values:
            self.values.append(i)

    def __call__(self):
        return self.values

class PTypes(PValues):
    pass

def p_start(p):
    '''start : create'''

    p[0] = p[1]


def p_create(p):
    '''create : CREATE create_body'''

    p[0] = p[2]
 
def p_create_body(p):
    '''create_body : TABLE NAME LPAREN values RPAREN'''

    p[0] = PCreate(p[2])
    p[0].set_vars(p[4])

def p_values(p):
    '''values : NAME type 
              | values COMMA NAME type'''

    value, vtype = 0, 0
    if len(p) == 3:

        p[0] = Vars()
        value, vtype = p[1:3]

    else:
    
        p[0] = p[1]
        value, vtype = p[3:5]

    p[0].append_values(value)
    p[0].append_types(vtype)


def p_type(p):
    '''type : int 
            | str
            | bol'''

    p[0] = p[1]

parser = yacc.yacc()

def build_tree(code):
    return parser.parse(code)