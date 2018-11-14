import os
import consts

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

	def is_file_exist(self):
		return os.path.isfile(self.__filename)