import os
import warnings
import shutil
import zipfile
import json
import filereader

class DataBase:

	metafile = filereader._PDBFileClass.meta

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
		with open(cur_dir+DataBase.metafile, "w") as meta:

			#Save meta info
			json.dump({
				"name": file_name,		#Database name
				"tables": []			#List of tables in DB
			}, meta)					#To meta file


		#Saving zip file:
		with zipfile.ZipFile(filename, "w") as database:
			database.write(cur_dir+DataBase.metafile, DataBase.metafile)

		shutil.rmtree(cur_dir, ignore_errors=True)	#Removing current directory
		return filereader._PDBFileClass(filename) 	#Returning file class

	@staticmethod
	def open(filename):
		#Opening database

		#Checking - is file exists:
		if not os.path.isfile(filename):

			#If not exist - create
			warnings.warn("File doesn't exist. Creating.")
			return DataBase.create(filename)

		return filereader._PDBFileClass(filename)	#Returning file class
