import pars

#s = '''CREATE TABLE test(int field, char field1)'''
s = '''CREATE test'''
result = pars.build_tree(s)
print (result)