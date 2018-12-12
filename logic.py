import binarydb
import dbparser.dbparse as parser


class DataBase(binarydb.BinaryDataBase):

	def exec(self, string):

		
		result = parser.build_tree(string)

		if result[0].type == "create":

			fields = {v: result[0].types[i] for i,  v in enumerate(result[0].values)}
			
			return self.create_table(result[0].name, fields)

		elif result[0].type == "show":
			return self.show_create(result[0].name)

		elif result[0].type == "select":
			
			print(result[1])
			print(result[0].type)
			print(result[0].select.name)
			print(result[0].select.fields)

			return self.select_from(result[0].select.name, result[0].select.fields)

		elif result[0].type == "insert":
			pass




x = DataBase("test.pdb")

#s = '''CREATE TABLE 'test' (V int, 'Value1' str, "Value2" bol, val integer, 'val1' string, "val2" bool)'''
#s = '''SHOW CREATE TABLE TEST'''
#s = '''SELECT value, value1 FROM test'''
s = '''SELECT (value, value1) FROM test WHERE value - -1 AND X OR Y'''
#s = '''SELECT (value, value1) FROM test WHERE (value - -1 AND X OR Y)'''
#s = '''SELECT (value, value1) FROM test WHERE (value - -1) AND (X OR Y)'''
#s = '''INSERT INTO 'test' (val1, val2)'''
#s = '''INSERT INTO 'test' VALUES(val1, val2)'''


x.exec(s)