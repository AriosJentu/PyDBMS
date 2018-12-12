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
			
			return self.select_from(
				result[0].select.name, 
				result[0].select.fields,
				result[1]
				)

		elif result[0].type == "insert":

			return self.insert_into(
				result[0].insert.name, 
				result[0].insert.fields
				)

		elif result[0].type == 'update':


			return self.update_set(
				result[0].name,
				result[0].values,
				result[0].fields,
				result[1]
			)

		elif result[0].type == 'delete':
			
			return self.delete_from(result[0].name, reuslt[1])
