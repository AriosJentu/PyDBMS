import binfile
import exceptions as exc
import consts
import classes

class DataBase(classes.Struct):

	def __init__(self, name):

		self._DBNAME = name														#Database file name
		self._FILE = False														#Opened binary file of database
		self._META = False			
		self._BINFILE = binfile.BinaryFile(name)										#Binary file of database


	def create_table(self, name, fields={}):

		if name in self:
			raise exc.DBTableException(0, name)

		self._FILE.seek(0, 2)

		meta = classes.TableMeta()
		meta.file = self._FILE
		meta.name = name

		meta.index = 16 + self._META.tblcount*classes.TableMeta.SIZE
		meta._fill_fields(fields)
		meta._calc_row_size()
		meta._write_to_file()

		self._META.tables[name] = meta
		self[name] = self._META.tables[name]									#Save table to struct indexes

		self._META._write_tables_count(self._META.tblcount+1)
		page = self.create_page(name)


	def create_page(self, tblname):

		if tblname not in self:
			raise exc.DBTableException(1, tblname)

		return self[tblname].create_page()


	def insert_into(self, tblname, values=[], fields=[]):
		
		if tblname not in self:
			raise exc.DBTableException(1, tblname)

		return self[tblname].insert(values, fields)

	def select_from(self, tblname, fields=[], expr="1"):

		if tblname not in self:
			raise exc.DBTableException(1, tblname)

		return self[tblname].select(fields, expr)

	def connect(self):

		if not self._BINFILE.is_file_exist():
			raise exc.DBFileException(1, self._DBNAME)		

		try:
			self._FILE = self._BINFILE.open("r+")
		except:
			raise exc.DBConnectionException(1)		


		#Check for signature
		cnt = self._FILE.readint(starts=0, cbytes=1)
		if self._FILE.readstr(starts=1, cbytes=cnt) != consts.signature:
			raise exc.DBFileException(3)

		self._META = classes.DataBaseMeta()
		self._META.file = self._FILE
		self._META._read_from_file()
		
		for i, v in self._META.tables.items():
			self[i] = v


	def close(self):
		self._FILE.close()


	def create(self):

		if not self._BINFILE.is_file_exist():
			self._FILE = self._BINFILE.open("w+")
		else:
			self._FILE = self._BINFILE.open("w+")
			#raise exc.DBFileException(0, self._DBNAME)		

		self._META = classes.DataBaseMeta()
		self._META.file = self._FILE
		self._META._write_to_file()

		#Fill tables meta
		for i in range(consts.tablecount):
			
			meta = classes.TableMeta()
			meta.index = 16 + i*classes.TableMeta.SIZE
			meta.file = self._FILE
			meta._write_to_file()	


		self.create_table("__test__", {
			"Test1": classes.Types.integer, 
			"Test2": classes.Types.string, 
			"Test3": classes.Types.bool
		})

	def get_tables(self):
		return self._META.tables


	def __getattr__(self, val):
		if val not in self.__dict__.keys():
			raise exc.DBTableException(1, val)

		return self[val]


db = DataBase("testdb2.jpdb")
db.create()
db.close()
db.connect()

db.create_table("Hello", {
	"Test": classes.Types.str,
	"Keks": classes.Types.int,
})
db.create_table("Hello2", {
	"Test1": classes.Types.int, 
	"Test2": classes.Types.str, 
	"Test3": classes.Types.bol
})

a = db.Hello.insert(["KEKSON"], ["Test"])
b = db.Hello.insert(["145"], ["Test"])
c = db.Hello.insert(["HELLO WORLD"], ["Test"])
d = db.Hello.insert(["Sasai Kudasai", 12], ["Test", "Keks"])

db.close()
db.connect()

"""
print(db._META.tables["__test__"], db.__test__.fields)
print(db.Hello, db.Hello.fields)
print(db.Hello2, db.Hello2.fields)
print()
print(classes.Types.int)
"""

db.Hello.delete("id < 2")
x = db.select_from("Hello", ["Keks", "Test", "__rowid__"], "1")
print(x)
print()

y = db.Hello.select(["*"], "__rowid__ > 2")
print(y)

print()
print("Removed:")
for i in db.Hello.get_rows(True):
	print(i)

#db.__test__.create_page()

"""
for i in db.__test__.get_pages():
	print(":", str(i))

print()

for i in db.Hello.get_pages():
	print(":", str(i))

print()

for i in db.__test__.ipages():
	print(i)
"""