import os
import warnings
import shutil
import zipfile
import json
import dbfiles
import consts

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
		with open(cur_dir+consts.meta, "w") as meta:

			#Save meta info
			json.dump({
				"name": file_name,		#Database name
				"tables": []			#List of tables in DB
			}, meta)					#To meta file


		#Saving zip file:
		with zipfile.ZipFile(filename, "w") as database:
			database.write(cur_dir+consts.meta, consts.meta)

		shutil.rmtree(cur_dir, ignore_errors=True)	#Removing current directory
		return dbfiles._PDBFileClass(filename) 	#Returning file class

	@staticmethod
	def open(filename):
		#Opening database

		#Checking - is file exists:
		if not os.path.isfile(filename):

			#If not exist - create
			warnings.warn("File doesn't exist. Creating.")
			return DataBase.create(filename)

		return dbfiles._PDBFileClass(filename)	#Returning file class
