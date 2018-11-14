import pars

s = '''CREATE TABLE 'test' (Value int, Value1 str, 'value2' bol)'''
#s = '''SHOW CREATE TABLE TEST'''
result = pars.build_tree(s)
print(result)