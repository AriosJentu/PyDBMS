import os
import warnings
import shutil
import zipfile
import json

class PDBFileClass:

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

		
		self.file = zipfile.ZipFile(filename, "r")
		self.file.extractall(cur_dir)

		self.filename = file_name+file_format
		self.current_dir = cur_dir
		self.files_list = []

		#Push all files inside array
		for i in self.file.filelist:

			#Check - is item not directory
			if os.path.isfile(cur_dir+i.filename):
				self.files_list.append(i.filename)

	def close(self):
		
		#Removing current directory
		shutil.rmtree(self.current_dir, ignore_errors=True)	
		
		self.file.close()

	def commit(self):
		
		#Close current file
		self.file.close()

		#And open it in write mode
		with zipfile.ZipFile(self.filename, "w") as db:
			for i in self.files_list:
				db.write(self.current_dir+i, i)

		#And reopen it in read mode
		self.file = zipfile.ZipFile(self.filename, "r")

	def open_file(self, filename, mode="r"):
		
		#--------------------------------------------
		#-- TODO: Create file in archive directory --
		#-- Save it's name in array -----------------
		#-- Return object with FILE class -----------
		#--------------------------------------------

		pass

	def create_directory(self, dirname):

		#----------------------------
		#-- TODO: Create directory --
		#----------------------------

		pass

	def remove_file(self, filename):

		#----------------------------------------------
		#-- TODO: Remove file from archive directory --
		#-- Remove it's name from array ---------------
		#----------------------------------------------

	def remove_directory(self, dirname):

		#----------------------------
		#-- TODO: Remove directory --
		#----------------------------

		pass

class DataBase:

	@staticmethod
	def create(filename):
		#Creating database

		#Checking - is file exists:
		if os.path.isfile(filename):
			warnings.warn("File exist. Rewriting.")

		#Getting file name and format:
		file_name = filename[:filename.find(".")]
		file_format = filename[filename.find("."):]

		cur_dir = ".__"+file_name+"__/"		#Current directory
		os.mkdir(cur_dir)					#Making base directory

		#Meta file creation
		with open(cur_dir+"meta.pkl", "w") as meta:

			#Save meta info
			json.dump({
				"name": filename,		#Database name
				"tables": []			#List of tables in DB
			}, meta)					#To meta file\


		#Saving zip file:
		with zipfile.ZipFile(filename, "w") as database:
			database.write(cur_dir+"meta.pkl", "meta.pkl")

		shutil.rmtree(cur_dir, ignore_errors=True)	#Removing current directory
		return PDBFileClass(filename) 				#Returning file class

	@staticmethod
	def open(filename):
		#Opening database

		#Checking - is file exists:
		if not os.path.isfile(filename):

			#If not exist - create
			warnings.warn("File doesn't exist. Creating.")
			return DataBase.create(filename)


		return PDBFileClass(filename)		#Returning file class

DataBase()
db = DataBase.open("database.jpdb")
print(db.files_list)
db.commit()
db.close()