import pytest
import binarydb
import exceptions as exc

database = binarydb.DataBase("testdbss.jpdb")
unexistdatabase = binarydb.DataBase("testdbsssss.jpdb")
database.create()

def test_connect_error():
	with pytest.raises(exc.DBConnectionException):
		database.connect()

	with pytest.raises(exc.DBFileException):
		unexistdatabase.connect()

def test_create_table_error():
	database.create_table("Hello", {"Kek": int})
	with pytest.raises(exc.DBTableException):
		database.create_table("Hello", {"Kek": int})

def test_insert():
	for i in range(10):
		database.Hello.insert([i], ["Kek"]) 
		database.Hello.insert([i+10], ["Kek"]) 
		
def test_select():

	select = database.Hello.select(["*"])
	assert select.count() == 20

	select = database.Hello.select(["*"], "id < 10")
	assert select.count() == 10

	select = database.Hello.select(["*"], "Kek%10 == 0 or Kek%5 == 1")
	assert select.count() == 6	#0, 10, 1, 6, 11, 16

def test_delete():

	database.Hello.delete("id >= 10")

	select = database.Hello.select(["*"])
	assert select.count() == 10

def test_insert_error():
	with pytest.raises(AttributeError):
		database.Hello.insert(["Kekos"], ["Kek"]) 
		database.Hello.insert(["KEKSON"], ["Faaka"]) 


