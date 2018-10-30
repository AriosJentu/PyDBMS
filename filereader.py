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

		
		#Private fields		
		self.__file = zipfile.ZipFile(filename, "r")
		self.__file.extractall(cur_dir)

		self.__filename = file_name+file_format
		self.__current_dir = cur_dir
		self.__filelist = set()

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
		with open(cur_dir+"meta.json", "w") as meta:

			#Save meta info
			json.dump({
				"name": filename,		#Database name
				"tables": []			#List of tables in DB
			}, meta)					#To meta file\


		#Saving zip file:
		with zipfile.ZipFile(filename, "w") as database:
			database.write(cur_dir+"meta.json", "meta.json")

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

