import os
import warnings
import shutil
import zipfile
import json

class PDBFileClass:

	def __init__(self, filename):
		
		#----------------------------------
		#-- TODO: Initializate archive ----
		#-- Get information about tables --
		#----------------------------------

		pass


class DataBase:

	@staticmethod
	def create(filename):
		#Creating database

		#Checking - is file exists:
		if os.path.isfile(filename+".jpdb"):
			warnings.warn("File exist. Rewriting.")

		#Making base directory
		os.mkdir("__"+filename+"__")

		#Current directory
		cur_dir = "__"+filename+"__/"

		#Meta file creation
		with open(cur_dir+"meta.pkl", "w") as meta:

			#Save meta info
			json.dump({
				"name": filename,		#Database name
				"tables": []			#List of tables in DB
			}, meta)					#To meta file

		#Saving zip file:
		with zipfile.ZipFile(filename+".jpdb","w") as database:
			database.write(cur_dir+"meta.pkl", "meta.pkl")

		#Removing current directory
		shutil.rmtree("__"+filename+"__/", ignore_errors=True)

		#Returning file class
		return PDBFileClass(filename)

	@staticmethod
	def open(filename):
		#Opening database

		#Checking - is file exists:
		if not os.path.isfile(filename+".jpdb"):
			warnings.warn("File doesn't exist. Creating.")
			return PDBWorkFile.create(filename)

		#Returning file class
		return PDBFileClass(filename)


db = DataBase.open("database")