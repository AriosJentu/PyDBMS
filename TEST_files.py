import pytest
import bindb
import exceptions as exc

database = bindb.BinaryDataBase("testdbss.jpdb")
unexistdatabase = bindb.BinaryDataBase("testdbsss.jpdb")

database.create()

def test_connect_error():
	with pytest.raises(exc.DBConnectionException):
		database.connect()	#Can't connect twice

def test_open_error():
	with pytest.raises(exc.DBFileException):
		unexistdatabase.connect()	#File doesn't exists

def test_create_error():
	with pytest.raises(exc.DBTableException):
		database.create_table("keks", ["Integer"], ["int"])
		database.create_table("keks", ["Another", "Other"], ["str", "int"])

def test_count_of_fields():
	with pytest.raises(exc.DBTableException):
		database.create_table("keks", ["Another"], ["str", "int"])	

def test_insert_error():
	with pytest.raises(exc.DBValueException):
		database.insert_item("keks", ["kek"])	#String, not int

def test_insert_fields_error():
	with pytest.raises(exc.DBValueException):
		database.insert_item("keks", [1, 2])	#Too much items

def test_insert_nothing_error():
	with pytest.raises(exc.DBValueException):
		database.insert_item("keks", [])	#Too few items

#----------LOCAL TEST

database = bindb.BinaryDataBase("testdb.jpdb")
database.create()
database.create_table("kekos", ["Lalka", "Palka", "Galka"], ["str", "int", "bol"])
database.create_table("keks", ["Integer"], ["int"])
database.create_page("keks")
database.create_page("kekos")
database.create_page("keks")

database.insert_item("kekos", ["Hello World", 12342, True])
database.insert_item("kekos", ["Use the force, Luke", 4343, False])
database.insert_item("kekos", ["You underestimate my power!!", 2435478, True])

print("All:")
for i in database.select_from("kekos", ["*"]):
	print("\t", i)

print("\nQuery:")
for i in database.select_from("kekos", ["*"], "len(Lalka) < 14 or Palka%2 == 0"):
	print("\t", i)

print("\nQuery:")
for i in database.select_from("kekos", ["*"], "len(Lalka) < 14"):
	print("\t", i)

print("\nQuery:")
for i in database.select_from("kekos", ["*"], "len(Lalka) > 14 and Palka%2 == 0"):
	print("\t", i)

print()
print(database.select_from("kekos", ["Galka", "Palka"]))
print(database.select_from("kekos", ["Lalka"]))
print(database.select_from("kekos", ["Palka"]))
print(database.select_from("kekos", ["Galka"]))

print("\nRemoved: ")
print(database.delete_from("kekos", "len(Lalka) > 14"))
print()

print(database.execute("show create table 'kekos'"))
print(database.execute("select Lalka, Palka from 'kekos'"))

print(database.get_list_of_tablenames())
for i in database.get_list_of_tablenames():
	print(database._get_table_meta(i))

print("\nAll:")
for i in database.select_from("kekos", ["*"]):
	print("\t", i)
