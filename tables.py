import warnings
import json

class _PDBTable:

	def __init__(self, database, tablename):

		self.__db = database
		self.__name = tablename