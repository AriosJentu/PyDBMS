import consts
import exceptions as exc

def where(expr, variables):
	return bool(
		eval(
			expr.lower(), 
			{
				v.lower(): variables[v] for v in variables.keys()
			}
		)
	)


#C-Struct Class
class Struct:

	def __init__(self, dictn={}):
		self.__dict__.update(**dictn)

	def __getattr__(self, val):	
		return self.__getitem__(val)

	def __getitem__(self, val):
		if val not in self.__dict__.keys():
			raise exc.DBException("Index '{}' doesn't exists.".format(val))

		return self.__dict__[val]

	def __setitem__(self, key, val):
		self.__dict__[key] = val

	def __iter__(self):
		for i in self.__dict__.keys():
			yield i

	def keys(self):
		return self.__dict__.keys()

	def values(self):
		return self.__dict__.values()

	def items(self):
		return self.__dict__.items()


class Type(Struct):

	def __init__(self, name, size, ctype, fullname):
		self.name = name
		self.size = size
		self.type = ctype
		self.fname = fullname

	def __str__(self):
		return "<Type " + self.fname+" [" + self.name + "] : " + (
			str(self.size) + " bytes>")

Types = Struct({
	"int": Type("int", consts.intsize, int, "integer"),
	"bol": Type("bol", consts.boolsize, bool, "bool"),
	"str": Type("str", consts.strsize, str, "string"),
})

Types.integer = Types.int
Types.bool = Types.bol
Types.string = Types.str

class DataBaseMeta(Struct):

	def __init__(self):

		self.tblcount = 0
		self.tables = Struct()
		self.file = False

	def _write_to_file(self):

		file = self.file

		#Write signatre
		file.writeint(13, starts=0, cbytes=1)
		file.writestr(consts.signature, starts=1, cbytes=13)
		file.writeint(self.tblcount, starts=14, cbytes=2)

		for i in self.tables:
			i._write_to_file(file)

	def _write_tables_count(self, count):
		self.tblcount = count
		self.file.writeint(self.tblcount, starts=14, cbytes=2)

	def _read_from_file(self):

		file = self.file

		#Check for signature
		cnt = file.readint(starts=0, cbytes=1)
		if file.readstr(starts=1, cbytes=cnt) != consts.signature:
			raise exc.DBFileException(3)

		self.tblcount = file.readint(starts=14, cbytes=2)

		for i in range(self.tblcount):
			meta = TableMeta()
			meta.index = 16 + i*TableMeta.SIZE
			meta.file = file
			meta._read_from_file()
			
			self.tables[meta.name] = meta

	def info(self):

		info = "\nDATABASE'S META INFORMATION:"
		cnt = "\nTables Count:\t" + str(self.tblcount)
		tabs = "\nTables Names:\t" + "[" + (
			", ".join(["'"+i+"'" for i in self.tables])
		) + "]"

		return info + cnt + tabs

	def __str__(self):
		return "<DataBase> {tables count: " + str(self.tblcount) + "}"

#Meta information about table
class TableMeta(Struct):

	SIZE = 32 + 17 + consts.fieldscount*24

	def __init__(self):
		
		self.name = ""
		self.index = -1
		self.file = False

		self.count = 0
		self.rmvdcnt = 0
		self.rowlen = 0

		self.firstpage = 0
		self.firstelmnt = 0
		self.firstrmvd = 0
		
		self.fields = []
		self.types = []

		self.positions = {"__rowid__": 1}

	def _write_to_file(self):

		stpos = self.index
		file = self.file

		file.writestr(self.name, starts=stpos, cbytes=32)
		
		self._update_pages()

		file.writeint(self.rowlen, starts=stpos+32+15, cbytes=2)
		file.writeint(len(self.fields), starts=stpos+32+17, cbytes=2)

		stpos += 32 + 17
		for i, v in enumerate(self.fields):
			file.writestr(v+self.types[i].name, starts=stpos, cbytes=24)
			stpos += 24

		#Fill by zeros
		size = TableMeta.SIZE-(stpos-self.index)
		file.writestr("", starts=stpos, cbytes=size)

	def _update_pages(self):

		stpos = self.index
		file = self.file

		file.writeint(self.count, starts=stpos+32, cbytes=3)
		file.writeint(self.rmvdcnt, starts=stpos+32+3, cbytes=3)
		file.writeint(self.firstpage, starts=stpos+32+6, cbytes=3)
		file.writeint(self.firstelmnt, starts=stpos+32+9, cbytes=3)
		file.writeint(self.firstrmvd, starts=stpos+32+12, cbytes=3)


	def _read_from_file(self):

		stpos = self.index
		file = self.file

		self.name = file.readstr(starts=stpos, cbytes=32)
		self.count = file.readint(starts=stpos+32, cbytes=3)
		self.rmvdcnt = file.readint(starts=stpos+32+3, cbytes=3)
		self.firstpage = file.readint(starts=stpos+32+6, cbytes=3)
		self.firstelmnt = file.readint(starts=stpos+32+9, cbytes=3)
		self.firstrmvd = file.readint(starts=stpos+32+12, cbytes=3)
		self.rowlen = file.readint(starts=stpos+32+15, cbytes=2)
		count = file.readint(starts=stpos+32+17, cbytes=2)

		stpos += 32 + 17
		pos = 4
		for i in range(count):
			field = file.readstr(starts=stpos+i*24, cbytes=21)
			ctype = Types[file.readstr(starts=stpos+i*24+21, cbytes=3)]
			
			self.fields.append(field)
			self.types.append(ctype)

			self.positions[field] = pos
			pos += ctype.size


	def _calc_row_size(self):

		self.rowlen = 4 #1 byte for existance and 3 for ID
		self.positions = {"__rowid__": 1}

		for i, v in enumerate(self.fields):
			self.positions[v] = self.rowlen
			self.rowlen += self.types[i].size

		self.rowlen += 6 #for previous item and next for 3 bytes


	def _fill_fields(self, fdict={}):
		self.fields = list(fdict.keys())
		self.types = list(fdict.values())


	def create_page(self):

		file = self.file

		pages = self.get_pages()
		file.seek(0, 2)

		index = file.tell()
		previndex = 0

		if len(pages) > 0:

			last_page = pages[-1]
			last_page.next = index
			last_page._update_to_file()
			previndex = last_page.index

		else:
			self.firstpage = index
			self._update_pages()
		
		page = TablePage(index)
		page.previous = previndex
		page.tblmeta = self
		page.file = file
		page._write_to_file()

		return page


	def get_pages(self):
		
		pages = []
		index = self.firstpage

		while index != 0:
			page = TablePage(index)
			page.file = self.file
			page.tblmeta = self
			page._read_from_file()
			index = page.next

			pages.append(page)

		return pages

	def ipages(self):
		index = self.firstpage

		while index != 0:
			
			page = TablePage(index)
			page.file = self.file
			page.tblmeta = self
			page._read_from_file()
			index = page.next

			yield page


	def get_removed(self):
		pass


	def insert(self, values=[], fields=[], where=""):

		pos, page = self._get_write_position()
		page.count += 1
		page._update_to_file()


	def _get_write_position(self):

		for i in self.get_pages():

			pos = i._get_write_position()
			if pos:
				return (pos, i)

		else:

			page = self.create_page()
			return (page._get_write_position(), page)

	def info(self):

		fields = [
			"'" + v + "' " + self.types[i].fname 
			for i, v in enumerate(self.fields)
		]
		
		poses = [
			"'" + i + "': " + str(v) for i, v in self.positions.items()
		]

		info = "\nTABLE META INFORMATION:"
		name = "\nName:\t\t\t\t{}".format(self.name)
		indx = "\nIndex:\t\t\t\t{}".format(self.index)
		cnt = "\nCount:\t\t\t\t{}".format(self.count)
		fpage = "\nFirst page at:\t\t{}".format(self.firstpage)
		fel = "\nFirst element at:\t{}".format(self.firstelmnt)
		frem = "\nFirst removed at:\t{}".format(self.firstrmvd)
		rlen = "\nRow Length:\t\t\t{}".format(self.rowlen)
		flds = "\nFields:\t\t\t\t["+", ".join(fields)+"]"
		poz = "\nPositions:\t\t\t["+ ", ".join(poses) + "]"

		return info + name + indx + cnt + fpage + fel + frem + rlen + flds + poz

	def __str__(self):

		return "<Table> {name: '" + self.name + "'" + \
			", meta_index: " + str(self.index) + \
			", count: " + str(self.count) + \
			", first_page: " + str(self.firstpage) + \
			", first_element: " + str(self.firstelmnt) + \
			", first_removed: " + str(self.firstrmvd) + \
			", row_length: " + str(self.rowlen) + \
			", fields_count: " + str(len(self.fields)) + \
		"}"


#Meta information about Page
class TablePage(Struct):

	def __init__(self, start):

		self.tblmeta = False
		self.index = start
		self.previous = 0
		self.next = 0
		self.count = 0
		self.file = False

	def _write_to_file(self):

		stpos = self.index
		file = self.file

		self._update_to_file()
		
		size = consts.pagesize*self.tblmeta.rowlen
		file.writeint(0, starts=stpos+12, cbytes=size)

	def _update_to_file(self):

		stpos = self.index
		file = self.file
		
		file.writeint(self.tblmeta.index, starts=stpos, cbytes=3)
		file.writeint(self.count, starts=stpos+3, cbytes=3)
		file.writeint(self.previous, starts=stpos+6, cbytes=3)
		file.writeint(self.next, starts=stpos+9, cbytes=3)

	def _read_from_file(self):

		stpos = self.index
		file = self.file

		self.count = file.readint(starts=stpos+3, cbytes=3)
		self.previous = file.readint(starts=stpos+6, cbytes=3)
		self.next = file.readint(starts=stpos+9, cbytes=3)

	def _get_write_position(self):

		if self.count >= consts.pagesize:
			return False
	
		stpos = self.index + 12
		npos = self.count*self.tblmeta.rowlen

		return stpos + npos

	def info(self):

		info = "\nTABLE'S PAGE META INFORMATION:"
		meta = "\nTable meta at:\t{}".format(self.tblmeta.index)		
		prev = "\nLocated at:\t{}".format(self.index)		
		prev = "\nPrevious at:\t{}".format(self.previous)		
		snext = "\nNext at:\t\t{}".format(self.next)		
		count = "\nCurrent count:\t{}".format(self.count)

		return info + meta + prev + snext + count	

	def __str__(self):
		return "<Page> {from: " + str(self.tblmeta.index) + \
			", index: " + str(self.index) + \
			", previous: " + str(self.previous) + \
			", next: " + str(self.next) + \
			", count: " + str(self.count) + \
		"}"


#Meta information about Row
class Row(Struct):

	def __init__(self):

		self.index = 0
		self.tblmeta = False
		self.file = False

		self.available = 0
		self.id = 0
		
		self.previous = 0
		self.next = 0
		self.values = Struct()

	def _write_to_file(self):

		stpos = self.index
		file = self.file
		size = self.tblmeta.rowsize

		file.writeint(self.available, starts=stpos, cbytes=1)
		file.writeint(self.id, starts=stpos+1, cbytes=3)

		for i in self.values:

			index = self.tblmeta.fields.index(i)
			otype = self.tblmeta.types[index].name

			file.writetype(
				otype.name,
				self.values[i],
				starts=stpos+v,
				cbytes=otype.size
			)

		file.writeint(self.previous, starts=size-6, cbytes=3)
		file.writeint(self.next, starts=size-3, cbytes=3)


	def _read_from_file(self):

		stpos = self.index
		file = self.file
		size = self.tblmeta.rowsize

		self.available = file.readint(starts=stpos, cbytes=1)
		self.id = file.readint(starts=stpos+1, cbytes=3)

		for i, v in self.tblmeta.positions.items():

			index = self.tblmeta.fields.index(i)
			otype = self.tblmeta.types[index].name

			self.values[i] = file.readtype(
				otype.name,
				starts=stpos+v,
				cbytes=otype.size
			)

		self.previous = file.readint(starts=size-6, cbytes=3)
		self.next = file.readint(starts=size-3, cbytes=3)




