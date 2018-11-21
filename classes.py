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

def format_items(dict):
	return ", ".join(
				[
					"'"+ i + "': " 
					+ str(v) 
					for i, v in dict.items() 
					if i[:2] != "__"
				]
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

	def __repr__(self):
		return "<Struct> {" + format_items(self) + "}"

	def keys(self):
		return self.__dict__.keys()

	def values(self):
		return self.__dict__.values()

	def items(self):
		return self.__dict__.items()

class Select(Struct):

	def __init__(self, fields=[]):
		self.fields = fields
		self.values = []

	def append(self, row):
		self.values.append(row)

	def __repr__(self):
		return "<Select Rows> {\n\tfields: " + (
			str(self.fields)
		) + "\n\tvalues:\n\t\t" + (
			"\n\t\t".join([str(i) for i in self.values])
		) + "\n}"



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

	SIZE = 32 + 22 + consts.fieldscount*24

	def __init__(self):
		
		self.name = ""
		self.index = -1
		self.file = False

		self.count = 0
		self.rmvdcnt = 0
		self.rowlen = 0

		self.firstpage = 0
		self.firstelmnt = 0
		self.lastelmnt = 0
		self.firstrmvd = 0
		
		self.fields = []
		self.types = []

		self.fcount = 0

		self.positions = {"__rowid__": 1}

	def _write_to_file(self):

		stpos = self.index
		file = self.file

		file.writestr(self.name, starts=stpos, cbytes=32)
		self._update_pages()
		file.writeint(self.rowlen, starts=stpos+32+18, cbytes=2)
		file.writeint(self.fcount, starts=stpos+32+20, cbytes=2)

		stpos += 32 + 22
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
		file.writeint(self.lastelmnt, starts=stpos+32+12, cbytes=3)
		file.writeint(self.firstrmvd, starts=stpos+32+15, cbytes=3)


	def _read_from_file(self):

		stpos = self.index
		file = self.file

		self.name = file.readstr(starts=stpos, cbytes=32)
		self.count = file.readint(starts=stpos+32, cbytes=3)
		self.rmvdcnt = file.readint(starts=stpos+32+3, cbytes=3)
		self.firstpage = file.readint(starts=stpos+32+6, cbytes=3)
		self.firstelmnt = file.readint(starts=stpos+32+9, cbytes=3)
		self.lastelmnt = file.readint(starts=stpos+32+12, cbytes=3)
		self.firstrmvd = file.readint(starts=stpos+32+15, cbytes=3)
		self.rowlen = file.readint(starts=stpos+32+18, cbytes=2)
		self.fcount = file.readint(starts=stpos+32+20, cbytes=2)

		stpos += 32 + 22
		pos = 4
		for i in range(self.fcount):
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
		self.fcount = len(self.fields)

	def _get_valid_fields(self, fields=[]):
		vals = []
		if "*" in fields:
			return self.fields

		for i in fields:
			if i in self.fields or i == "__rowid__":
				vals.append(i)

		return vals

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
		page._write_to_file()

		return page


	def get_pages(self):
		
		pages = []
		index = self.firstpage

		while index != 0:
			page = TablePage(index)
			page.tblmeta = self
			page._read_from_file()
			index = page.next

			pages.append(page)

		return pages

	def ipages(self):
		index = self.firstpage

		while index != 0:
			
			page = TablePage(index)
			page.tblmeta = self
			page._read_from_file()
			index = page.next

			yield page


	def irows(self, removed=False):

		#Returning almost unreaded rows (only indexes)
		if removed:
			index = self.firstrmvd
		else:
			index = self.firstelmnt
	
		while index != 0:

			row = Row(index)
			row.tblmeta = self
			row._read_indexes()
			index = row.next

			yield row

	def get_rows(self, removed=False, fields=[]):

		rows = []
		for i in self.irows(removed):
			i._read_from_file(fields)
			rows.append(i)

		return rows


	def insert(self, values=[], fields=[]):

		if self.firstrmvd:
			
			r_row = Row(self.firstrmvd)
			r_row.tblmeta = self
			r_row._read_indexes()
			r_row.next = 0
			r_row._write_indexes()

			pos = self.firstrmvd
			self.firstrmvd = r_row.previous

		else:

			pos, page = self._get_write_position()
			page.count += 1
			page._update_to_file()
		
		if not self.firstelmnt:
			self.firstelmnt = pos
		else:
			prevrow = Row(self.lastelmnt)
			prevrow.tblmeta = self
			prevrow._read_indexes()
			prevrow.next = pos
			prevrow._write_indexes()

		row = Row(pos)
		row.tblmeta = self
		row.id = self.count
		row.available = 1
		row.next = 0
		row.previous = self.lastelmnt
		row.values = Struct({v:values[i] for i, v in enumerate(fields)})
		row._write_to_file()

		self.count += 1
		self.lastelmnt = pos
		self._update_pages()


	def select(self, fields=[], expr="1"):

		fields = self._get_valid_fields(fields)
		selects = Select(fields)

		for i in self.get_rows():

			if where(expr, i.values):
				i._select_by_fields(fields)
				selects.append(i)

		return selects

	def delete(self, expr="1"):

		index = self.firstelmnt

		while index != 0:

			cur_row = Row(index)
			cur_row.tblmeta = self
			cur_row._read_from_file()
			saved = index
			index = cur_row.next

			if where(expr, cur_row.values):
				
				#Inverse: next means previous, and previous means next! (Reading/writing backward)
				
				if saved == self.firstelmnt:
					self.firstelmnt = cur_row.next

				cur_row._drop_row()
				cur_row.available = 2
				cur_row.previous = 0
				cur_row.next = self.firstrmvd
				cur_row._write_indexes()
				
				self.firstrmvd = saved
				self._update_pages()


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

		inf = "\nTABLE META INFORMATION:"
		n = "\nName:\t\t\t\t{}".format(self.name)
		i = "\nIndex:\t\t\t\t{}".format(self.index)
		cnt = "\nCount:\t\t\t\t{}".format(self.count)
		fp = "\nFirst page at:\t\t{}".format(self.firstpage)
		fel = "\nFirst element at:\t{}".format(self.firstelmnt)
		lel = "\nLast element at:\t{}".format(self.lastelmnt)
		fr = "\nFirst removed at:\t{}".format(self.firstrmvd)
		rl = "\nRow Length:\t\t\t{}".format(self.rowlen)
		fc = "\nFields count:\t\t{}".format(self.fcount)
		fl = "\nFields:\t\t\t\t["+", ".join(fields)+"]"
		p = "\nPositions:\t\t\t["+ ", ".join(poses) + "]"

		return inf + n + i + cnt + fp + fel + lel + fr + rl + fc + fl + p

	def __str__(self):

		return "<Table> {name: '" + self.name + "'" + \
			", meta_index: " + str(self.index) + \
			", count: " + str(self.count) + \
			", first_page: " + str(self.firstpage) + \
			", first_element: " + str(self.firstelmnt) + \
			", last_element: " + str(self.lastelmnt) + \
			", first_removed: " + str(self.firstrmvd) + \
			", row_length: " + str(self.rowlen) + \
			", fields_count: " + str(self.fcount) + \
		"}"


#Meta information about Page
class TablePage(Struct):

	def __init__(self, start):

		self.tblmeta = False
		self.index = start
		self.previous = 0
		self.next = 0
		self.count = 0

	def _write_to_file(self):

		stpos = self.index
		file = self.tblmeta.file

		self._update_to_file()
		
		size = consts.pagesize*self.tblmeta.rowlen
		file.writeint(0, starts=stpos+12, cbytes=size)

	def _update_to_file(self):

		stpos = self.index
		file = self.tblmeta.file
		
		file.writeint(self.tblmeta.index, starts=stpos, cbytes=3)
		file.writeint(self.count, starts=stpos+3, cbytes=3)
		file.writeint(self.previous, starts=stpos+6, cbytes=3)
		file.writeint(self.next, starts=stpos+9, cbytes=3)

	def _read_from_file(self):

		stpos = self.index
		file = self.tblmeta.file

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

	def __init__(self, index=0):

		self.index = index
		self.tblmeta = False

		self.available = 0
		self.id = 0
		
		self.previous = 0
		self.next = 0
		self.values = Struct()
		self.values.id = self.id

	def _drop_row(self):

		if self.previous:

			prev = Row(self.previous)
			prev.tblmeta = self.tblmeta
			prev._read_indexes()
			prev.next = self.next
			prev._write_indexes()

		if self.next:

			rnxt = Row(self.next)
			rnxt.tblmeta = self.tblmeta
			rnxt._read_indexes()
			rnxt.previous = self.previous
			rnxt._write_indexes()


	def _select_by_fields(self, fields=[]):

		fields = self.tblmeta._get_valid_fields(fields)
		
		if not fields or type(fields) != list:
			fields = self.tblmeta.fields

		res = Struct()
		for i in fields:
			if i in self.values:
				res[i] = self.values[i]

		self.values = res
		if "__rowid__" in fields:
			self.values.id = self.id


	def _write_to_file(self):

		stpos = self.index
		file = self.tblmeta.file

		self._write_indexes()

		for i in self.values:

			index = self.tblmeta.fields.index(i)
			otype = self.tblmeta.types[index]
			v = self.tblmeta.positions[i]

			file.writetype(
				otype.name,
				self.values[i],
				starts=stpos+v,
				cbytes=otype.size
			)


	def _read_from_file(self, fields=[]):

		fields = self.tblmeta._get_valid_fields(fields)

		if not fields or type(fields) != list:
			fields = self.tblmeta.fields

		stpos = self.index
		file = self.tblmeta.file

		self._read_indexes()
		for i, v in self.tblmeta.positions.items():

			if i not in fields:
				continue

			index = self.tblmeta.fields.index(i)
			otype = self.tblmeta.types[index]

			self.values[i] = file.readtype(
				otype.name,
				starts=stpos+v,
				cbytes=otype.size
			)


	def _read_indexes(self):

		stpos = self.index
		file = self.tblmeta.file
		size = stpos+self.tblmeta.rowlen

		self.available = file.readint(starts=stpos, cbytes=1)
		self.id = file.readint(starts=stpos+1, cbytes=3)
		self.previous = file.readint(starts=size-6, cbytes=3)
		self.next = file.readint(starts=size-3, cbytes=3)
		self.values.id = self.id
		self.values.__rowid__ = self.id


	def _write_indexes(self):

		stpos = self.index
		file = self.tblmeta.file
		size = stpos+self.tblmeta.rowlen

		file.writeint(self.available, starts=stpos, cbytes=1)
		file.writeint(self.id, starts=stpos+1, cbytes=3)
		file.writeint(self.previous, starts=size-6, cbytes=3)
		file.writeint(self.next, starts=size-3, cbytes=3)

	def info(self):

		info = "\nROW'S META INFORMATION:"
		#meta = "\nTable meta at:\t{}".format(self.tblmeta.index)		
		#prev = "\nLocated at:\t{}".format(self.index)		
		#prev = "\nPrevious at:\t{}".format(self.previous)		
		#snext = "\nNext at:\t\t{}".format(self.next)		
		#count = "\nCurrent count:\t{}".format(self.count)

		#return info + meta + prev + snext + count	
		return info

	def __str__(self):
		return "<Row> {from: " + str(self.tblmeta.index) + \
			", index: " + str(self.index) + \
			", id: " + str(self.id) + \
			", available: " + str(self.available) + \
			", previous: " + str(self.previous) + \
			", next: " + str(self.next) + \
			" : " + format_items(self.values) + \
		"}"