import os
import consts

#Default switch function to types for getting type bytesize
def get_type_size(types):
	return {
		True: consts.maxsize,
		(types == "int"): consts.intsize,
		(types == "str"): consts.strsize
	}[True]


#Exception class
class DataBaseException(Exception):

	def __init__(self, message):
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

	def connect(self):
		
		if os.path.isfile(self.__name):
			return self.open()
		else:
			return self.create()

	def create(self):

		#if os.path.isfile(self.__name):
		#	raise DataBaseException("File already exists.")

		name = self.__name
		
		with self.__file.open("w") as file:

			#Writing signature 
			file.writeint(15) 								#Write size of signature to 1st byte from 0th (to start)
			file.writestr(consts.signature, cbytes=15)		#Write 15 bytes from 1st

			#Write DataBase name:
			fname = name[:name.rfind(".")]		#Get dbname from filename 
			file.writestr(fname, cbytes=31)		#Write 31 bytes for filename

			#Write tables count (48th byte) [MAX Count of tables = 32 (255 max int in 1 byte)]
			file.writeint(2, starts=47, cbytes=1)	#1 is tables count (now it's just test table)

			#Write meta info for 32 tables
			for i in range(consts.tablecount):

				if i <= 1:

					table = {
						"name": "__test"+str(i)+"__",
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

				index = 48 + 512*i
				#Write table name and count of fields
				file.writestr(table["name"], starts=index, cbytes=31)	#Requred TableName size is 31 (from 48th byte)
				file.writeint(len(table["fields"]), starts=index+31)			#Write 1 byte to count of fields
				
				#Write fields, max count of fields is 15
				index += 32
				for j in range(14):
					
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
				file.writeint(0, starts=index, cbytes=30) 	#Index size - 3 bytes, can be 10 indexes,it means 5 pages, last 2 bytes are size of row
				file.writeint(rowlength, starts=index+30, cbytes=2)	#Row size

			rowlength = 1 + 3 + consts.intsize + consts.strsize #Recalculate
			index += 32		#Skip last line (because it's busy)

			#Write it's table 
			for i in range(consts.pagesize):
				rowindex = index + i*rowlength
				file.writeint(0, starts=rowindex, cbytes=rowlength)

			#Get end of page
			rowindex += rowlength


		return self.open()

	def open(self):

		#if not os.path.isfile(self.__name):
		#	raise DataBaseException("File doesn't exists.")
		
		name = self.__name
		
		with self.__file.open("r") as file:

			#Getting signature
			size = file.readint(starts=0)				#Read 1 byte from 0th (Size could be 16)
			sign = file.readstr(starts=1, cbytes=size)	#Read string from next "size" bytes, starts from 1th
			
			#Checking for binary signature
			if sign != consts.signature:
				raise DataBaseException("Wrong Signature")

			dbname = file.readstr(starts=16, cbytes=31)	#Read 31 bytes of name starts after signature (16th byte)

			#Getting tables count
			self.__tables_count = file.readint(starts=47)


	#Getting tables count
	def get_tables_count(self):
		return self.__tables_count


	def _get_table_meta(self, tablename):

		with self.__file.open("r") as file:
			
			#Search table from file
			for i in range(self.__tables_count):

				#Get table name from index
				tabindex = 48 + 512*i
				name = file.readstr(starts=tabindex, cbytes=31)
				print(name)
				
				#Check tablename for correctness				
				if name == tablename:

					tabindex += 32	#Skip name
					
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

					#Calculate row length
					rowlength = 1 + 3 + sum(get_type_size(i) for i in meta["types"])
					meta["rowlength"] = rowlength

					return meta




database = BinaryDataBase("testdb.jpdb")
database.create()
print(database._get_table_meta("__test1__"))