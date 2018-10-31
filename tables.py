import warnings
import json
import consts

class _PDBTable:

	def __init__(self, database, tablename):

		self.__db = database			#Database connected to work with table
		self.__filename = tablename		#Table name (File)
		self.__name = tablename			#Table name

		self.__fields = ["__rowid__"]	#Primary field

		#Open meta file of table to parse real name and fields
		with self.__db._open_file(
			self.__name+"/"+consts.meta
		) as metafile:

			parse = json.load(metafile)
			self.__name = parse["name"]
			self.__fields += parse["fields"]
			

	def drop_table(self):
		
		#Drop table as table method, used from default database method
		return self.__db.drop_table(self.__filename)


	def show_create(self):

		fields = self.__fields[1:]
		#Query for table creation
		query = (
			"CREATE TABLE `" + self.__filename + "` (\n" +
			"\t\t\t\t\t`" + '`, `'.join(fields) + "`\n"
			"\t\t\t\t" + ");"
		)

		#Return string of table showing create table
		return (
			"===================================================" + "\n" +
			'\t\tTable:\t"' + self.__name + '"\n' +
			"\t   Fields:\t" + '["' + '", "'.join(fields) + '"]' + "\n"
			" Create Table:\t" + query + "\n" +
			"==================================================="
		)