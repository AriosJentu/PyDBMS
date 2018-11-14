import pars

"""
CREATE TABLE 'name' (field1 type1, "field2" type2)
SHOW CREATE TABLE 'name'
SELECT field1, 'field2' FROM 'table' WHERE cond
INSERT INTO 'table' VALUES (val1, val2)
INSERT INTO 'table' (val1, val2)
DELETE FROM 'table' WHERE cond
UPDATE 'table' SET field1=val1, 'field2'='val2' WHERE cond
"""

#s = '''CREATE TABLE 'test' (Value int, 'Value1' str, "value2" bol)'''
#s = '''SHOW CREATE TABLE TEST'''
#s = '''SELECT value, value1 FROM test'''
#s = '''SELECT (value, value1) FROM test'''

s = '''INSERT INTO 'test' (val1, val2)'''
result = pars.build_tree(s)
print(result)