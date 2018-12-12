import binfile
import exceptions as exc
import consts
import classes

class BinaryDataBase(classes.Struct):

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


	def is_db_opened(self):
		return self._META != False and self._BINFILE.is_file_exist()


	def _check_for_opened(self):
		if not self.is_db_opened():
			raise exc.DBConnectionException(0)


	def create_table(self, name, fields={}):

		self._check_for_opened()
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

		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].create_page()


	def show_create(self, tblname):

		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].show_create()


	def insert_into(self, tblname, values=[], fields=[]):
		
		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].insert(values, fields)


	def insert_into_after(self, tblname, row, values=[], fields=[]):
		
		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].insert_after(row, values, fields)


	def select_from(self, tblname, fields=[], expr="1", removed=False, upd_inc=False):

		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].select(fields, expr, removed, upd_inc)


	def update_set(self, tblname, values=[], fields=[], expr="1"):

		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].update(values, fields, expr)


	def update_set_insecure(self, tblname, values=[], fields=[], expr="1"):

		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].update_insecure(values, fields, expr)


	def delete_from_insecure(self, tblname, expr="1"):

		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].delete_insecure(expr)


	def delete_from(self, tblname, expr="1"):

		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].delete(expr)


	def delete_row_from(self, tblname, row, expr="1"):

		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].delete_row(row, expr)


	def commit_for(self, tblname):

		self._check_for_opened()
		self._check_table_name(tblname)
		return self[tblname].commit()


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
		self._check_for_opened()
		self._FILE.close()
		self._FILE = False


	def create(self, recreate=False):

		if recreate or not self._BINFILE.is_file_exist():
			self._FILE = self._BINFILE.open("w+")
		else:
			raise exc.DBFileException(0, self._DBNAME)		

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
		self._check_for_opened()
		return self._META.tables


	def __getattr__(self, val):
		if val not in self.__dict__.keys():
			raise exc.DBTableException(1, val)

		return self[val]