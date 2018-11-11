import os
import consts
import exceptions as exc
import parser

#Default switch function to types for getting type bytesize
available_types = ["int", "str", "bol"] 										#Available types
metasize = (consts.fieldscount+2)*32

def get_type_size(types):
	return {
		True: consts.maxsize,
		(types == "bol"): consts.boolsize,
		(types == "int"): consts.intsize,
		(types == "str"): consts.strsize,
	}[True]

def get_type_from_str(types):
	return {
		True: None,
		(types == "bol"): bool,
		(types == "int"): int,
		(types == "str"): str,
	}[True]

def get_default_value(types):
	return {
		True: None,
		(types == "bol"): False,
		(types == "int"): 0,
		(types == "str"): "",
	}[True]


#Class to work with binary file like as default file 
class BinaryFile:

	#Class for Binary File

	#Initializer (Open File)
	def __init__(self, filename):

		self.__filename = filename
		self.__file = None

	def open(self, ftype="r"):
		self.__file = open(self.__filename, ftype+"b")
		return self

	#Default functions of Binary File:
	def close(self):
		self.__file.close()
		self.__file = None

	def __enter__(self):
		return self

	def __exit__(self, *args):
		return self.close()

	def read(self, cbytes):
		return self.__file.read(cbytes)

	def tell(self):
		return self.__file.tell()

	def seek(self, offset, whence=0):
		return self.__file.seek(offset, whence)

	#Custom functions:
	def writestr(self, string, starts=-1, cbytes=1):
		#Inserting string, converted to bytes, to file with fixed bytes count

		#Making substring
		string = string[:cbytes]
		zeros = consts.binzero * (cbytes - len(string))

		#Check for starting
		if starts >= 0:
			self.seek(starts)

		#Write info to file
		return self.__file.write(zeros+string.encode())

	def writeint(self, intg, starts=-1, cbytes=1, signed=False):
		#Inserting integer, converted to bytes, to file with fixed bytes count

		#Convert integer to bytes
		number = intg.to_bytes(cbytes, "little")

		#Check for starting
		if starts >= 0:
			self.seek(starts)
		
		#Write info to file
		return self.__file.write(number)

	def writebool(self, boolval, starts=-1, cbytes=1):
		#Inserting boolean value converted to integer
		return self.writeint(int(boolval), starts, cbytes)

	def readstr(self, starts=-1, cbytes=1):
		#Getting bytes from file, converted to string with fixed bytes count

		#Check for starting
		if starts >= 0:
			self.seek(starts)

		#Getting string
		string = self.__file.read(cbytes).replace(consts.binzero, b"")

		#Return string
		return string.decode()

	def readint(self, starts=-1, cbytes=1, signed=False):
		#Getting bytes from file, converted to int with fixed bytes count

		#Check for starting
		if starts >= 0:
			self.seek(starts)

		#Getting integer
		intbytes = bytes(self.__file.read(cbytes))
		ints = int.from_bytes(intbytes, "little")

		#Return string
		return ints

	def readbool(self, starts=-1, cbytes=1):
		#Read boolean value as integer
		return bool(self.readint(starts, cbytes)) 

	def writetype(self, otype, *args, **kwargs):
		#Write to file from type of object

		if otype == "int":
			self.writeint(*args, **kwargs)
		elif otype == "str":
			self.writestr(*args, **kwargs)
		elif otype == "bol":
			self.writebool(*args, **kwargs)

	def readtype(self, otype, *args, **kwargs):
		#Read from file as type of object

		if otype == "int":
			return self.readint(*args, **kwargs)
		elif otype == "str":
			return self.readstr(*args, **kwargs)
		elif otype == "bol":
			return self.readbool(*args, **kwargs)


#Class for binary database
class BinaryDataBase:

	def __init__(self, name):

		self.__name = name
		self.__file = BinaryFile(name)
		self.__tables_count = 1
		self.__opened = False

	def create(self):

		#if os.path.isfile(self.__name):
		#	raise exc.DBFileException(0, self.__name)							#File Exist

		name = self.__name
		
		with self.__file.open("w") as file:

			#Writing signature 
			file.writeint(15) 													#Write size of signature to 1st byte from 0th (to start)
			file.writestr(consts.signature, cbytes=15)							#Write 15 bytes from 1st

			#Write DataBase name:
			fname = name[:name.rfind(".")]										#Get dbname from filename 
			file.writestr(fname, cbytes=31)										#Write 31 bytes for filename

			#Write tables count (48th byte) [MAX Count of tables = 32 (255 max int in 1 byte)]
			file.writeint(1, starts=47, cbytes=1)								#1 is tables count (now it's just test table)

			#Write meta info for 32 tables
			for i in range(consts.tablecount):

				if i == 0:

					table = {
						"name": "__test__",
						"fields": ["test1", "test2"],
						"types": ["int", "str"]
					}
					rowlength = 1 + 3 + consts.intsize + consts.strsize			#Existing checker, hidden identifier, and size of columns types

				else:

					table = {
						"name": "",
						"fields": [],
						"types": []
					}
					rowlength = 0

				#Calculate index of current table in file
				index = 48 + metasize*i
				#Write table name and count of fields
				file.writestr(table["name"], starts=index, cbytes=28)			#Requred TableName size is 28 (from 48th byte)
				file.writeint(0, starts=index+28, cbytes=3)						#Write count of items in db
				file.writeint(len(table["fields"]), starts=index+31)			#Write 1 byte to count of fields

				#Write fields, max count of fields is consts.fieldscount
				index += 32
				for j in range(consts.fieldscount):
					
					#Get Field
					try:
						#Join field name and it's type to one string (last 3 bytes is type)
						text = table["fields"][j][:29] + table["types"][j][:3]

					except:
						text = ""

					#Get index of field name position
					index_pos = index + j*32
					file.writestr(text, starts=index_pos, cbytes=32)

				#Write information about positions
				index = index_pos+32											#Add last line
				file.writeint(0, starts=index, cbytes=30) 						#Index size - 3 bytes, can be 10 indexes, last 2 bytes are size of row
				file.writeint(rowlength, starts=index+30, cbytes=2)				#Row size

			rowlength = 1 + 3 + consts.intsize + consts.strsize 				#Recalculate
			findex = 48 + (consts.fieldscount+1)*32								#Calculate line with tables indexes
			index += 32															#Skip last line (because it's busy)

			#Write index of start
			file.writeint(index, starts=findex, cbytes=3)
			
			#Write it's table 
			for i in range(consts.pagesize):
				rowindex = index + i*rowlength
				file.writeint(0, starts=rowindex, cbytes=rowlength)

			#Get end of page
			rowindex += rowlength

		return self.connect()

	def connect(self):

		#Check for opened table:
		if self.__opened:
			raise exc.DBConnectionException(1)									#Database already connected

		#Check for existance
		if not os.path.isfile(self.__name):
			raise exc.DBFileException(1, self.__name)							#File doesn't exist
		
		with self.__file.open("r") as file:

			#Getting signature
			size = file.readint(starts=0)										#Read 1 byte from 0th (Size could be 16)
			sign = file.readstr(starts=1, cbytes=size)							#Read string from next "size" bytes, starts from 1th
			
			#Checking for binary signature
			if sign != consts.signature:
				raise exc.DBFileException(3)									#Wrong signature

			dbname = file.readstr(starts=16, cbytes=31)							#Read 31 bytes of name starts after signature (16th byte)

			#Getting tables count
			self.__tables_count = file.readint(starts=47)
			self.__opened = True


	def create_table(self, tablename, fields=[], types=[]):

		#Check for opened table:
		if not self.__opened:
			raise exc.DBConnectionException(0)									#Database isn't connected

		#Check for max tables:
		if self.__tables_count >= consts.tablecount:
			raise exc.DBFileException(2)										#Maximal tables in Database

		#Check for existing name
		if tablename in self.get_list_of_tablenames():
			raise exc.DBTableException(0, tablename)							#Name already exist

		#Generate correct types
		types = [i for i in types if i.lower() in available_types]

		#Check for length of arrays
		if len(fields) != len(types):
			raise exc.DBValueException(0)										#Wrong count of fields and types

		#Check for fields count
		if len(fields) > consts.fieldscount:
			raise exc.DBTableException(2)										#Too much fields

		table = {
			"name": tablename,
			"fields": fields,
			"types": types,
		}

		#Calculate new table meta info position
		tabindex = 48 + metasize*self.__tables_count

		#Open file
		with self.__file.open("r+") as file:

			saved = tabindex
			file.writestr(table["name"], starts=tabindex, cbytes=28)			#Requred TableName size is 28
			file.writeint(0, starts=tabindex+28, cbytes=3)						#Write count of items in table
			file.writeint(len(table["fields"]), starts=tabindex+31)				#Write 1 byte to count of fields
			
			tabindex += 32														#Append line to tab index

			#Write fields
			for j, v in enumerate(fields):
				
				#Check type for availablety
				if not get_type_from_str(types[j]):
					raise exc.DBTableException(3, types[j])						#Field type doesn't exist

				#Join field name and it's type to one string (last 3 bytes is type)
				text = v[:29] + types[j]

				#Get index of field name position
				index_pos = tabindex + j*32
				file.writestr(text, starts=index_pos, cbytes=32)

			rowlength = 4 + sum([get_type_size(i) for i in types])				#Calculate sizes
			tabindex += consts.fieldscount*32									#Get to the last part of meta info of table

			file.seek(0, 2)														#Get file Cursor to the end of file
			findex = file.tell()												#Get EOF index
			
			#Write index of start
			file.writeint(findex, starts=tabindex, cbytes=3)
			file.writeint(rowlength, starts=tabindex+30, cbytes=2)

			#Write page meta info
			file.writeint(0, starts=findex, cbytes=2)							#Save count of fields in meta
			file.writeint(0, starts=findex+2, cbytes=2)						#Save count of removed fields in meta
			file.writeint(saved, starts=findex+4, cbytes=2)					#Save table meta position
			
			#Write table's first page  
			findex += 6
			for i in range(consts.pagesize):
				rowindex = findex + i*rowlength
				file.writeint(0, starts=rowindex, cbytes=rowlength)

		self.__tables_count += 1												#Append one table to tables count


	def _create_page_from_table_index(self, tabindex):

		#Check for opened table:
		if not self.__opened:
			raise exc.DBConnectionException(0)									#Database isn't connected

		#Open file
		with self.__file.open("r+") as file:

			#Get table name from index
			name = file.readstr(starts=tabindex, cbytes=31)

			#Index of array of positions
			index_pos = tabindex + (consts.fieldscount+1)*32

			#Cycle for all indexes of pages
			for i in range(10):

				#Check for zero
				if file.readint(starts=index_pos+3*i, cbytes=3) == 0:

					#Save index
					pos = index_pos+3*i
					break

			#If cycle is not broken
			else:
				raise exc.DBPageException(0, name)								#Count of page too much

			#Read length of row
			rowlength = file.readint(starts=index_pos+30, cbytes=2)

			#Calculate file positions
			file.seek(0, 2)														#Get to the end of file
			last_index = file.tell()

			#Write page index to table meta info
			file.writeint(last_index, starts=pos, cbytes=3)
			
			#Write page meta info
			file.writeint(0, starts=last_index, cbytes=2)							#Save count of fields in meta
			file.writeint(0, starts=last_index+2, cbytes=2)						#Save count of removed fields in meta
			file.writeint(tabindex, starts=last_index+4, cbytes=2)					#Save table meta position

			#Write page to the end of file
			last_index += 6
			for i in range(consts.pagesize):
				rowindex = last_index + i*rowlength
				file.writeint(0, starts=rowindex, cbytes=rowlength)

			return last_index													#return byteindex of page in file


	def create_page(self, tablename):

		#Check for opened table:
		if not self.__opened:
			raise exc.DBConnectionException(0)									#Database isn't connected
		
		tabs = self.get_list_of_tablenames()
		if tablename in tabs.keys():
			return self._create_page_from_table_index(tabs[tablename])

		else:
			raise exc.DBTableException(1, tablename)							#Table doesn't exist


	def _get_meta_from_index(self, tabindex):
			
		with self.__file.open("r") as file:
	
			#Check for opened table:
			if not self.__opened:
				raise exc.DBConnectionException(0)								#Database isn't connected

			#Get table name from index
			name = file.readstr(starts=tabindex, cbytes=28)
			itemscnt = file.readint(starts=tabindex+28, cbytes=3)
			
			#Returnable meta information
			meta = {
				"index": tabindex,
				"name": name,
				"count": itemscnt,
				"fields": [],
				"types": [],
				"pagespos": [], 												#Only start positions
				"rowlength": 0,
			}

			tabindex += 32														#Skip name
			

			fieldscnt = file.readint(starts=tabindex-1)							#Read count of fieldscnt
			
			#Read fields
			for j in range(fieldscnt):

				index_pos = tabindex + j*32
				field = file.readstr(starts=index_pos, cbytes=29)				#Get field
				stype = file.readstr(starts=index_pos+29, cbytes=3)				#Get type
				meta["fields"].append(field)
				meta["types"].append(stype)


			index_pos = tabindex + consts.fieldscount*32
			for i in range(10):
				
				indx = index_pos + i*3											#Calculate index
				pageindx = file.readint(starts=indx, cbytes=3)					#Read position of start page number 'i'
				
				#Check for existing page index
				if pageindx == 0:
					break

				#Save start position to page's positions array
				meta["pagespos"].append(pageindx)

			rowlength = file.readint(starts=index_pos+30, cbytes=2)				#Read rowlength from meta
			meta["rowlength"] = rowlength

			return meta


	def _get_table_meta(self, tablename):

		#Check for opened table:
		if not self.__opened:
			raise exc.DBConnectionException(0)									#Database isn't connected
		
		tabs = self.get_list_of_tablenames()
		if tablename in tabs.keys():
			return self._get_meta_from_index(tabs[tablename])

		else:
			raise exc.DBTableException(1, tablename)							#Table doesn't exist


	def insert_item(self, tablename, values=[]):

		#Check for opened table:
		if not self.__opened:
			raise exc.DBConnectionException(0)									#Database isn't connected
		
		#Get table meta information
		meta = self._get_table_meta(tablename)

		#Check for size of values equal to size of fields
		if len(values) != len(meta["fields"]):
			raise exc.DBValueException(1, len(meta["fields"]), len(values))		#Incorrect values count

		#Check for types
		for i, v in enumerate(values):

			#If it isn't none and types are not equal
			if type(v) != get_type_from_str(meta["types"][i]) and v != None:
			
				#Send exception
				raise exc.DBValueException(2, 
					i,
					str(get_type_from_str(meta["types"][i])),
					str(type(v)), 
				)

			#If value is None
			elif v == None:
				#Write default value
				values[i] = get_default_value(meta["types"][i])

		#Calculate index
		"""
		pagenumber = meta["count"]//consts.pagesize								#Calculate page, where to insert
		onpageindex = meta["count"]%consts.pagesize								#Calculate index on page

		#If page number is equal to count of pages - create new page (cuz index doesn't exists)
		if pagenumber == len(meta["pagespos"]):
			index = self._create_page_from_table_index(meta["index"])
			meta["pagespos"].append(index)

		"""

		with self.__file.open("r+") as file:

			#Calculate indexes
			if len(meta["pagespos"]) == 0:
				
				pagepos = self._create_page_from_table_index(meta["index"])
				count = 0
				rcount = 0
			
			else:

				#Read every pages indexes
				for i in meta["pagespos"]:

					pagepos = i 												#Set page
					rcount = file.readint(starts=pagepos, cbytes=2)				#Read count of elements on page
					count = rcount + file.readint(starts=pagepos+2, cbytes=2)

					#Check for count
					if count < consts.pagesize:
						break

			#Check for count elements on page
			if count >= consts.pagesize:
				pagepos = self._create_page_from_table_index(meta["index"])		#Create table if count of elements higher than available elements
				count = 0														#On empty page there is no elements
			
			#Calculate positions
			value_pos = pagepos + count*meta["rowlength"] + 6					#Calculate index on page

			#Append count of elements
			file.writeint(meta["count"]+1, starts=meta["index"]+28, cbytes=3)	#To meta information about table
			file.writeint(rcount+1, starts=pagepos)									#To meta information about page

			#Write existance and identifier
			file.writeint(1, starts=value_pos)									#1 means existance
			file.writeint(meta["count"], starts=value_pos+1, cbytes=3)			#Count is index

			value_pos += 4

			#Write values	
			for i, v in enumerate(values):

				#Type of value
				otype = meta["types"][i]

				#Calculate current bytes count
				bytescnt = get_type_size(otype)

				#Write info to file
				file.writetype(otype, v, starts=value_pos, cbytes=bytescnt)

				#Append position
				value_pos += bytescnt


	def _get_one_row(self, tableindex, rowid=0, findexes=[], meta=False):

		#Check for opened table:
		if not self.__opened:
			raise exc.DBConnectionException(0)									#Database isn't connected

		#Get table meta information
		if not meta:
			meta = self._get_meta_from_index(tableindex)

		#Calculate page indexes
		pageid = rowid//consts.pagesize
		tabindx = rowid%consts.pagesize

		#Get byteindex of page and of item
		pageindx = meta["pagespos"][pageid]
		readpos = pageindx + tabindx*meta["rowlength"] + 6
		print("READING FROM: ", readpos)

		#Read file
		with self.__file.open("r") as file:
			
			#Result array
			res = []

			#Read all indexes of fields
			for i in findexes:

				#Calculate type, start and size of information
				ftype = meta["types"][i[2]]				
				start = readpos+i[0]
				size = i[1]
				
				#Read info
				obj = file.readtype(ftype, starts=start, cbytes=size)
				
				#Write to array
				res.append(obj)

			#Return array
			return res

	def select_from(self, tablename, fields=[], rtype="array"):

		#Check for opened table:
		if not self.__opened:
			raise exc.DBConnectionException(0)									#Database isn't connected

		#Get table meta information
		meta = self._get_table_meta(tablename)

		#If select all, set fields index
		if fields[0] == "*":
			fields = meta["fields"]

		#Create array of fields information - shifting, bytescount and type id
		indexes = [[0, 0, " "] for _ in fields]
		byteindx = 4															#Start from (current byteindex)

		#Get all fields
		for i, v in enumerate(meta["fields"]):

			#Find size of type
			size = get_type_size(meta["types"][i])
			
			#If field in argument
			if v in fields:
				#Insert shifting index, bytescount to array and index of type
				indexes[fields.index(v)] = [byteindx, size, i]

			#Append size to current byteindex
			byteindx += size

		#If type of presentation is array
		if rtype == "array":
	
			#Result array of select
			results = []
			
			#Read data
			for i in range(meta["count"]):

				#Get by one rows
				results.append(self._get_one_row(
					meta["index"],
					i,
					indexes,
					meta
				))

			return results

	def show_create(self, tablename):

		#Check for opened table:
		if not self.__opened:
			raise exc.DBConnectionException(0)									#Database isn't connected

		#Get table meta information
		meta = self._get_table_meta(tablename)

		fields = meta["fields"]
		types = meta["types"]
		typearr = ["`%s` %s"%(fields[i], types[i]) for i in range(len(types))]

		query = (
			"CREATE TABLE `" + meta["name"] + "` (\n" +
			"\t\t\t\t\t`" + ', '.join(typearr) + "`\n"
			"\t\t\t\t" + ");"
		)

		return (
			"===================================================" + "\n" +
			'\t\tTable:\t"' + meta["name"] + '"\n' +
			"\t   Fields:\t" + '["' + '", "'.join(fields) + '"]' + "\n"
			"\t    Types:\t" + '["' + '", "'.join(types) + '"]' + "\n"
			" Create Table:\t" + query + "\n" +
			"==================================================="
		)


	def get_list_of_tablenames(self):

		#Check for opened table:
		if not self.__opened:
			raise exc.DBConnectionException(0)									#Database isn't connected

		names = {}
		with self.__file.open("r") as file:
			
			#Search table from file
			for i in range(self.__tables_count):

				#Get table name from index
				tabindex = 48 + metasize*i
				name = file.readstr(starts=tabindex, cbytes=28)
				names[name] = tabindex

		return names

	def execute(self, sqlquery):

		if sqlquery.lower().find("show create") >= 0:
			
			query = parser.Parser.show_create_basic(sqlquery)["show"]
			return self.show_create(query["name"])

		elif sqlquery.lower().find("create") >= 0:
			pass

		elif sqlquery.lower().find("select") >= 0:

			query = parser.Parser.select_basic(sqlquery)["select"]
			print(query)
			return self.select_from(query["table"], query["values"])

		elif sqlquery.lower().find("insert") >= 0:
			pass