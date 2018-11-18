import binfile
import exceptions as exc
import consts
import classes

def where(expr, variables):
	return bool(
		eval(
			expr.lower(), 
			{
				v.lower(): variables[v] for v in variables.keys()
			}
		)
	)

class BinaryDataBase:

	def __init__(self, name):

		self.name = name
		self.db = binfile.BinaryFile(name)
		self.file = False
		self.meta = False

	def create_table(self, name, fields={}):

		self.file.seek(0, 2)

		meta = classes.TableMeta()
		meta.file = self.file
		meta.name = name

		meta.index = 16 + self.meta.tblcount*classes.TableMeta.SIZE
		meta.firstpage = self.file.tell()
		meta.fill_fields(fields)
		meta.calc_row_size()
		meta.write_to_file()
		print(meta)
		print(meta.get_pages())

		page = classes.TablePage(meta.firstpage)
		page.tblmeta = meta
		page.file = self.file
		page.write_to_file()
		print(page)

		self.meta.write_tables_count(self.meta.tblcount+1)
		
		return meta

	def connect(self):

		if not self.db.is_file_exist():
			raise exc.DBFileException(1, self.name)		

		try:
			self.file = self.db.open("r+")
		except:
			raise exc.DBConnectionException(1)		


		#Check for signature
		cnt = self.file.readint(starts=0, cbytes=1)
		if self.file.readstr(starts=1, cbytes=cnt) != consts.signature:
			raise exc.DBFileException(3)

		self.meta = classes.DataBaseMeta()
		self.meta.file = self.file
		self.meta.read_from_file()


	def close(self):
		self.file.close()


	def create(self):

		if not self.db.is_file_exist():
			self.file = self.db.open("w+")
		else:
			self.file = self.db.open("w+")
			#raise exc.DBFileException(0, self.name)		

		self.meta = classes.DataBaseMeta()
		self.meta.file = self.file
		self.meta.write_to_file()

		#Fill tables meta
		for i in range(consts.tablecount):
			
			meta = classes.TableMeta()
			meta.index = 16 + i*classes.TableMeta.SIZE
			meta.file = self.file
			meta.write_to_file()				

		self.create_table("__test__", {
			"Test1": classes.Types.integer, 
			"Test2": classes.Types.string, 
			"Test3": classes.Types.bool
		})

		self.create_table("__test2__", {
			"Tests1": classes.Types.integer, 
			"Testss2": classes.Types.string, 
			"Tests3": classes.Types.bool
		})

db = BinaryDataBase("testdb2.jpdb")
db.create()
db.close()
db.connect()
print(classes.TableMeta.SIZE)