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
        self.type = "create"

        self.values = []
        self.types = []
        
    def set_vars(self, vars_):
        
        self.values = vars_.vars[0]
        self.types = vars_.vars[1]


class PShow(PCreate):

    def __init__(self, name=""):

        self.name = name
        self.type = "show"

    def set_vars(self, *args): pass


class PSelect(Struct):

    def __init__(self, select_body, where_body):
        self.type = "select"
        self.select = select_body
        self.where = where_body


class PSelectBody(Struct):

    def __init__(self, name=""):

        self.name = name
        self.fields = []
    
    def set_fields(self, fields):
        self.fields = fields


class PWhereBody(Struct):

    def __init__(self):

        self.fields = []
        self.operators = []
        self.statements = []

    def set_where_body(self, *values):

        self.fields = values[0][0]
        self.operators = values[0][1]
        self.statements = values[0][2]


class PInsert(PSelect):
    pass


class PVars:
    def __init__(self):
        self.vars = [[], []]

    def append_values(self, *values):
        self.vars[0].append(*values)
        

    def append_types(self, *types):
        self.vars[1].append(*types)
        

def p_start(p):
    '''start : create
             | show
             | select
             | insert'''

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

        p[0] = PVars()
        value, vtype = p[1:3]

    else:
    
        p[0] = p[1]
        value, vtype = p[3:5]

    p[0].append_values(value)
    p[0].append_types(vtype)


def p_show(p):
    '''show : SHOW CREATE TABLE NAME'''

    p[0] = PShow(p[4])


def p_select(p):
    '''select : SELECT select_body 
              | SELECT select_body where_body'''
    if len(p) == 3:
        p[0] = PSelect(p[2], [])
    else:
        p[0] = PSelect(p[2], p[3])

    
def p_select_body(p):
    '''select_body : fields FROM NAME
                   | LPAREN fields RPAREN FROM NAME'''

    fields, name = 0, 0
    
    if len(p) == 4:

        fields = 1
        name = 3

    else:

        fields = 2
        name = 5

    
    p[0] = PSelectBody(p[name])
    p[0].set_fields(p[fields])


def p_where_body(p):
    '''where_body : WHERE where_condition'''

    p[0] = PWhereBody()

    p[0].set_where_body(p[2])

def p_where_condition(p):
    '''where_condition : field operator statement
                       | where_condition connecting_operator field operator statement'''

    field, operator, statement = 0, 0, 0
    p[0] = [[], [], []]

    if len(p) == 4:

        field = 1
        operator = 2
        statement = 3
    else:

        p[0] = p[1]

        field = 3
        operator = 4
        statement = 5

    p[0][0].append(p[field])
    p[0][1].append(p[operator])
    p[0][2].append(p[statement])

def p_field(p):
    '''field : NAME'''

    p[0] = p[1]

def p_connecting_operator(p):
    '''connecting_operator : OR
                           | NOR
                           | NAND
                           | AND '''

    p[0] = p[1]

def p_operator(p):
    '''operator : EQUAL
                | NOT_EQUAL
                | GREATER_THAN
                | LESS_THAN
                | GREATER_THAN_OR_EQUAL
                | LESS_THAN_OR_EQUAL
                | BETWEEN 
                | LIKE
                | IN
                | OR
                | NOR
                | NOT
                | NAND
                | AND
                | PLUS
                | MINUS
                | MUL
                | TRUE_DIV
                | FLOOR_DIV
                | PERCENT
                | POWER'''

    p[0] = p[1]


def p_statement(p):
    '''statement : NAME'''

    p[0] = p[1]


def p_insert(p):
    '''insert : INSERT insert_body'''

    p[0] = p[2]


def p_insert_body(p):
    '''insert_body : INTO NAME LPAREN fields RPAREN
                   | INTO NAME VALUES LPAREN fields RPAREN'''

    fields, name = 0, 2
    p[0] = PInsert(p[name])

    if len(p) == 6:
        fields = 4
        
    else:
        fields = 5

    p[0].set_fields(p[fields])


def p_fields(p):
    '''fields : NAME
              | fields COMMA NAME'''

    field = 0

    if len(p) == 2:

        p[0] = []
        field = 1

    else:

        p[0] = p[1]
        field = 3

    p[0].append(p[field])


def p_type(p):
    '''type : int 
            | str
            | bol'''

    p[0] = p[1]


parser = yacc.yacc()

def build_tree(code):

    result = []

    start = code.index('WHERE') + 6
    finish = len(code)

    result.append(code[start:finish])
    result.append(parser.parse(code))
    



    return result