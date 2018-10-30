import os
import warnings
import shutil
import zipfile
import json
import table

class _PDBFileClass:

	#Meta file name
	meta = "meta.json"

	def __init__(self, filename):
	
		#Getting file name and format:
		file_name = filename[:filename.find(".")]
		file_format = filename[filename.find("."):]

		cur_dir = ".__"+file_name+"__/"		#Current directory
		
		#Check for existing directory
		if os.path.isdir(cur_dir):
			warnings.warn("File was opened.")

		else:
			os.mkdir(cur_dir)				#Making base directory

		
		#Private fields		
		self.__file = zipfile.ZipFile(filename, "r")
		self.__file.extractall(cur_dir)

		self.__dbname = file_name
		self.__filename = file_name+file_format
		self.__current_dir = cur_dir

		self.__filelist = set()
		self.__metainfo = self.get_meta_info()

		#Push all files inside array
		for i in self.__file.filelist:

			#Check - is item not directory
			if os.path.isfile(cur_dir+i.filename):
				self.__filelist.add(i.filename)


	def close(self, remove=True):
		
		#Removing current directory
		if remove:
			shutil.rmtree(self.__current_dir, ignore_errors=True)	
		
		self.__file.close()


	def commit(self):
		
		#Close current file
		self.__file.close()

		#And open it in write mode
		with zipfile.ZipFile(self.__filename, "w") as db:

			#Write all files from filelist
			for i in self.__filelist:
				db.write(self.__current_dir+i, i)

		#And reopen it in read mode
		self.__file = zipfile.ZipFile(self.__filename, "r")


	#Methods what do not recommend to use by users
	def _create_file(self, filename):
		
		realfilename = self.__current_dir+filename

		#Checking - is file exists:
		if os.path.exists(realfilename):
			warnings.warn("File exist. Recreating.")

		#Try to create file
		try:
			open(realfilename, "w").close()		#Create file

		#If it can't be created, send warning
		except:
			warnings.warn("Can't create file here. Check for directory.")
			return None

		self.__filelist.add(filename) 			#Save file in set

	def _open_file(self, filename, mode="r"):

		realfilename = self.__current_dir+filename
		
		#Trying to open file from this archieve
		try:
			return open(realfilename, mode)

		except:
			warnings.warn("File doesn't exist. Can't open.")


	def _create_directory(self, dirname):

		dirname = self.__current_dir+dirname

		#Checking - is directory exists:
		if os.path.isdir(dirname):
			warnings.warn("Directory exist. Pass.")

		else:
			#Try to create directory
			try:
				os.mkdir(dirname)

			#If it can't be created, send warning
			except:
				warnings.warn("Can't create directory here.")



	def _remove_file(self, filename):

		#Check is filename is directory
		realfilename = self.__current_dir+filename

		if os.path.isdir(realfilename):
			warnings.warn("Can't remove. This is directory.")

		#If file is not exists
		elif not os.path.isfile(realfilename):
			warnings.warn("File doesn't exist. Can't remove.")

		#If filename is file
		else:
			self.__filelist.remove(filename)	#Remove from array
			os.remove(realfilename)				#Remove file


	def _remove_directory(self, dirname):

		realdirname = self.__current_dir+dirname

		#Check is filename is directory
		if os.path.isdir(realdirname):

			psize = len(dirname) 	#Pattern size
			
			#Regenerating file list
			self.__filelist = set([
				i 
				for i in self.__filelist 
				if i[:psize] != dirname
			])

			#Removing requested directory
			shutil.rmtree(realdirname, ignore_errors=True)

		else:
			warnings.warn("Directory doesn't exist. Can't remove.")



	def _is_file_exist(self, filename):
		#Function to check existance of file as class method
		return os.path.isfile(self.__current_dir+filename)


	def _is_directory_exist(self, dirname):
		#Function to check existance of directory as class method
		return os.path.isdir(self.__current_dir+dirname)

	def get_file_list(self):
		return self.__filelist

	def get_current_directory(self):
		return self.__current_dir


	def get_meta_info(self):
		
		#Check archive for is it a database (has it meta file)
		if not os.path.isfile(self.__current_dir+_PDBFileClass.meta):
			raise Exception("This archive is not database")

		#Read meta and return dict with fields "name" and "tables"
		#with open(self.__current_dir+_PDBFileClass.meta) as dbmeta:
		with self._open_file(_PDBFileClass.meta) as metafile:

			self.__metainfo = json.load(metafile)
			return self.__metainfo


	def _update_meta_info(self, diction={}):

		#Meta file of db must contain only 2 meta informations: name and tables 
		#Check for name in database
		if "name" not in diction.keys():
			name = self.__dbname
		else:
			name = diction["name"]

		#Check for tables in database
		if "tables" not in diction.keys() or type(diction["tables"]) != type([]):
			tables = []
		else:
			tables = diction["tables"]

		#Update meta info
		self.__metainfo = {"name": name, "tables": tables}

		#Update file
		with self._open_file(_PDBFileClass.meta, "w") as metafile:

			#Save meta info
			json.dump(self.__metainfo, metafile)


	def is_table_exist(self, name):

		#Get list of tables
		tables = self.get_meta_info()["tables"]

		#Flag for existance
		flag = True

		#If name not in meta file tables info
		if name not in tables:
			flag = False

		#----------------------------------------
		#-- TODO: Check directory existance -----
		#-------- Check in directory meta file --
		#----------------------------------------

		return flag


	def create_table(self, name, fields=[]):

		#Check table for existance
		if self.is_table_exist(name):
			warnings.warn("Table already exists.")
			return None

		#Update meta information of database
		metainfo = self.get_meta_info()
		metainfo["tables"].append(name)
		self._update_meta_info(metainfo)

		#Creating directory for database and it's meta
		self._create_directory(name)
		self._create_file(name+"/"+_PDBFileClass.meta)

		#Save information of table to it's meta file
		with self._open_file(name+"/"+_PDBFileClass.meta, "w") as tabmeta:
			
			json.dump({
				"name": name,			#Name of table
				"fields": fields		#Table fields
			}, tabmeta)					#To meta file


		return table._PDBTable(self, name)


	def get_table(self, name):
		
		#Check table for existance
		if not self.is_table_exist(name):
			warnings.warn("Table isn't exists.")
			return None

		#If table exists, returns table object
		return table._PDBTable(self, name)

