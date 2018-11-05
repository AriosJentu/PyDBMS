import os
import consts

#Default switch function to types for getting type bytesize
available_types = ["int", "str"] #Available types
metasize = (consts.fieldscount+2)*32

def get_type_size(types):
	return {
		True: consts.maxsize,
		(types == "int"): consts.intsize,
		(types == "str"): consts.strsize
	}[True]

#Exception class
class DataBaseException(Exception):

	Exist = "{} '{}' already exist."
	DoesntExist = "{} '{}' doesn't exist."

	Exceptions = {

		0:	"Data Base Error",
		1:	Exist.format("File", "{}"),
		2:	DoesntExist.format("File", "{}"),
		3:	Exist.format("Table", "{}"),
		4:	DoesntExist.format("Table", "{}"),
		5:	"Wrong Data Base Signature.",
		6:	"Data Base isn't connected.",
		7:	"Already too much tables inside.",
		8:	"Count of fields and count of types are different",
		9:	"Too much Table's Fields",

	}
	
	def __init__(self, message, *args):
		
		ex = DataBaseException.Exceptions
		if type(message) == int and 0 <= message < len(ex):
			super().__init__(ex[message].format(*args))
		else:
			super().__init__(message)

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


#Class for binary database
class BinaryDataBase:

	def __init__(self, name):

		self.__name = name
		self.__file = BinaryFile(name)
		self.__tables_count = 1
		self.__opened = False

	def connect(self):
		
		if os.path.isfile(self.__name):
			return self.open()
		else:
			return self.create()

	def create(self):

		#if os.path.isfile(self.__name):
		#	raise DataBaseException(1, self.__name)	#File Exist

		name = self.__name
		
		with self.__file.open("w") as file:

			#Writing signature 
			file.writeint(15) 								#Write size of signature to 1st byte from 0th (to start)
			file.writestr(consts.signature, cbytes=15)		#Write 15 bytes from 1st

			#Write DataBase name:
			fname = name[:name.rfind(".")]		#Get dbname from filename 
			file.writestr(fname, cbytes=31)		#Write 31 bytes for filename

			#Write tables count (48th byte) [MAX Count of tables = 32 (255 max int in 1 byte)]
			file.writeint(1, starts=47, cbytes=1)	#1 is tables count (now it's just test table)

			#Write meta info for 32 tables
			for i in range(consts.tablecount):

				if i == 0:

					table = {
						"name": "__test__",
						"fields": ["test1", "test2"],
						"types": ["int", "str"]
					}
					rowlength = 1 + 3 + consts.intsize + consts.strsize	#Existing checker, hidden identifier, and size of columns types

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
				file.writestr(table["name"], starts=index, cbytes=31)	#Requred TableName size is 31 (from 48th byte)
				file.writeint(len(table["fields"]), starts=index+31)	#Write 1 byte to count of fields
				
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
				index = index_pos+32 #Add last line
				file.writeint(0, starts=index, cbytes=30) 	#Index size - 3 bytes, can be 10 indexes, last 2 bytes are size of row
				file.writeint(rowlength, starts=index+30, cbytes=2)	#Row size

			rowlength = 1 + 3 + consts.intsize + consts.strsize #Recalculate
			findex = 48 + (consts.fieldscount+1)*32	#Calculate line with tables indexes
			index += 32								#Skip last line (because it's busy)

			#Write index of start
			file.writeint(index, starts=findex, cbytes=3)
			
			#Write it's table 

			#file.writeint(253, starts=index, cbytes=1)					####TESTING

			for i in range(consts.pagesize):
				rowindex = index + i*rowlength
				file.writeint(0, starts=rowindex, cbytes=rowlength)
			
			#file.writeint(253, starts=rowindex+rowlength-1, cbytes=1)	####TESTING

			#Get end of page
			rowindex += rowlength

		return self.open()

	def open(self):

		#Check for existance
		if not os.path.isfile(self.__name):
			raise DataBaseException(2, self.__name)		#File doesn't exist
		
		with self.__file.open("r") as file:

			#Getting signature
			size = file.readint(starts=0)				#Read 1 byte from 0th (Size could be 16)
			sign = file.readstr(starts=1, cbytes=size)	#Read string from next "size" bytes, starts from 1th
			
			#Checking for binary signature
			if sign != consts.signature:
				raise DataBaseException(5)				#Wrong signature

			dbname = file.readstr(starts=16, cbytes=31)	#Read 31 bytes of name starts after signature (16th byte)

			#Getting tables count
			self.__tables_count = file.readint(starts=47)
			self.__opened = True


	def create_table(self, tablename, fields=[], types=[]):

		#Check for opened table:
		if not self.__opened:
			raise DataBaseException(6)	#Database isn't connected

		#Check for max tables:
		if self.__tables_count >= consts.tablecount:
			raise DataBaseException(7)	#Maximal tables in Database

		#Generate correct types
		types = [i for i in types if i.lower() in available_types]

		#Check for length of arrays
		if len(fields) != len(types):
			raise DataBaseException(8)	#Wrong count of fields and types

		#Check for fields count
		if len(fields) > consts.fieldscount:
			raise DataBaseException(9)	#Too much fields

		table = {
			"name": tablename,
			"fields": fields,
			"types": types
		}

		#Calculate new table meta info position
		tabindex = 48 + metasize*self.__tables_count

		#Open file
		with self.__file.open("r+") as file:

			file.writestr(table["name"], starts=tabindex, cbytes=31)	#Requred TableName size is 31 (from 48th byte)
			file.writeint(len(table["fields"]), starts=tabindex+31)		#Write 1 byte to count of fields
			
			tabindex += 32	#Append line to tab index

			#Write fields
			for j, v in enumerate(fields):
				
				#Join field name and it's type to one string (last 3 bytes is type)
				text = v[:29] + types[j]

				#Get index of field name position
				index_pos = tabindex + j*32
				file.writestr(text, starts=index_pos, cbytes=32)

			rowlength = 4 + sum([get_type_size(i) for i in types])	#Calculate sizes
			tabindex += consts.fieldscount*32	#Get to the last part of meta info of table

			file.seek(0, 2)						#Get file Cursor to the end of file
			findex = file.tell()				#Get EOF index
			
			#Write index of start
			file.writeint(findex, starts=tabindex, cbytes=3)
			file.writeint(rowlength, starts=tabindex+30, cbytes=2)
			
			#Write it's table 
			for i in range(consts.pagesize):
				rowindex = findex + i*rowlength
				file.writeint(0, starts=rowindex, cbytes=rowlength)

			#file.writeint(254, starts=findex, cbytes=1)				###TESTING
			#file.writeint(254, starts=rowindex+rowlength-1, cbytes=1)	###TESTING

		self.__tables_count += 1	#Append one table to tables count


	def _get_meta_from_index(self, tabindex):
			
		with self.__file.open("r") as file:
	
			#Check for opened table:
			if not self.__opened:
				raise DataBaseException(6)	#Database isn't connected

			#Get table name from index
			name = file.readstr(starts=tabindex, cbytes=31)

			tabindex += 32	#Skip name
			
			#Returnable meta information
			meta = {
				"name": name,
				"fields": [],
				"types": [],
				"pagespos": [], 	#Only start positions
				"rowlength": 0
			}

			fieldscnt = file.readint(starts=tabindex-1)	#Read count of fieldscnt
			
			#Read fields
			for j in range(fieldscnt):

				index_pos = tabindex + j*32
				field = file.readstr(starts=index_pos, cbytes=29)	#Get field
				stype = file.readstr(starts=index_pos+29, cbytes=3)	#Get type
				meta["fields"].append(field)
				meta["types"].append(stype)


			index_pos = tabindex + consts.fieldscount*32
			for i in range(10):
				
				indx = index_pos + i*3								#Calculate index
				pageindx = file.readint(starts=indx, cbytes=3)		#Read position of start page number 'i'
				
				#Check for existing page index
				if pageindx == 0:
					break

				#Save start position to page's positions array
				meta["pagespos"].append(pageindx)

			rowlength = file.readint(starts=index_pos+30, cbytes=2)	#Read rowlength from meta
			meta["rowlength"] = rowlength

			return meta


	def _get_table_meta(self, tablename):

		#Check for opened table:
		if not self.__opened:
			raise DataBaseException(6)	#Database isn't connected
		
		tabs = self.get_list_of_tablenames()
		if tablename in tabs.keys():
			return self._get_meta_from_index(tabs[tablename])

		else:
			raise DataBaseException(4, tablename)	#Table doesn't exist

	def get_list_of_tablenames(self):

		#Check for opened table:
		if not self.__opened:
			raise DataBaseException(6)	#Database isn't connected

		names = {}
		with self.__file.open("r") as file:
			
			#Search table from file
			for i in range(self.__tables_count):

				#Get table name from index
				tabindex = 48 + 512*i
				name = file.readstr(starts=tabindex, cbytes=31)
				names[name] = tabindex

		return names




database = BinaryDataBase("testdb.jpdb")
database.create()
database.create_table("keks", ["Integer"], ["int"])
print(database.get_list_of_tablenames())
for i in database.get_list_of_tablenames():
	print(database._get_table_meta(i))