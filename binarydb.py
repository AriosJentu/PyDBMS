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


	def _check_table_name(self, name, nots=False):
		if not nots:
			if name not in self:
				raise exc.DBTableException(1, name)
		else:
			if name in self:
				raise exc.DBTableException(0, name)


	def create_table(self, name, fields={}):

		self._check_table_name(name, True)

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

		self._check_table_name(tblname)
		return self[tblname].create_page()


	def insert_into(self, tblname, values=[], fields=[]):
		
		self._check_table_name(tblname)
		return self[tblname].insert(values, fields)


	def select_from(self, tblname, fields=[], expr="1"):

		self._check_table_name(tblname)
		return self[tblname].select(fields, expr)


	def update_set(self, tblname, values=[], fields=[], expr="1"):

		self._check_table_name(tblname)
		return self[tblname].update(values, fields, expr)

	def connect(self):

		if not self._BINFILE.is_file_exist():
			raise exc.DBFileException(1, self._DBNAME)		

		if self._FILE: raise exc.DBConnectionException(1)
		self._FILE = self._BINFILE.open("r+")


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
		self._FILE = False


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
			"Test1": int, 
			"Test2": str, 
			"Test3": bool
		})

	def get_tables(self):
		return self._META.tables


	def __getattr__(self, val):
		if val not in self.__dict__.keys():
			raise exc.DBTableException(1, val)

		return self[val]

#TESTING

db = DataBase("testdb2.jpdb")
db.create()
db.close()
db.connect()

db.create_table("Hello", {
	"Test": str,
	"Keks": int,
})

def decor(func):
	def wrapper(inputs, *args, removed=False):

		print()
		print(inputs+":")
		func(*args)
		sel = db.Hello.select("*", removed=removed)
		print(sel)
		print("rempos: " + str(db.Hello.lastrmvd))
		print("fpos: " + str(db.Hello.firstelmnt))
		print("lpos: " + str(db.Hello.lastelmnt))

	return wrapper

for i in range(8):
	db.Hello.insert(["Kek", i])

insert = decor(db.Hello.insert)
remove = decor(db.Hello.delete)
update = decor(db.Hello.update)
passed = decor(lambda: 0)

passed("INSERTING 8 ELEMENTS")
remove("REMOVING 1", "id < 3")
remove("REMOVING 2", "id >= 6")
passed("ALREADY REMOVED ELEMENTS", removed=True)
insert("INSERTING 1", ["Kekos", 11])
update("UPDATING", ["Lalka", 12], ["*"], "id >= 3")
passed("AFTER UPDATING")
insert("INSERTING 2", ["Kekos", 13])
passed("REMOVED AFTER INSERT", removed=True)
remove("REMOVING ALL", "1")
passed("NOW ALL TABLE")
passed("NOW ALL REMOVED ELEMENTS IN TABLE", removed=True)
