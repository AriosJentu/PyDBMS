try:
	import dbparser.dbparse as parse
except:
	import dbparse as parse
import re

"""
CREATE TABLE 'name' (field1 type1, "field2" type2)
SHOW CREATE TABLE 'name'
SELECT field1, 'field2' FROM 'table' WHERE cond
INSERT INTO 'table' VALUES (val1, val2)
INSERT INTO 'table' (val1, val2)
DELETE FROM 'table' WHERE cond
UPDATE 'table' SET field1=val1, 'field2'='val2' WHERE cond
"""


#s = '''CREATE TABLE 'test' (V int, 'Value1' str, "Value2" bol, val integer, 'val1' string, "val2" bool)'''
#s = '''SHOW CREATE TABLE TEST'''
#s = '''SELECT value, value1 FROM test'''
#s = '''SELECT (value, value1) FROM test WHERE value - -1 AND X OR Y'''
#s = '''SELECT (value, value1) FROM test WHERE (value - -1 AND X OR Y)'''
#s = '''SELECT (value, value1) FROM test WHERE (value - -1) AND (X OR Y)'''
#s = '''INSERT INTO 'test' (val1, val2)'''
s = '''INSERT INTO 'test' VALUES (val1, val2)'''


tree = parse.build_tree(s)

print(tree[1])
print(tree[0].type)
print(tree[0].insert.name)
print(tree[0].insert.fields)
print()






