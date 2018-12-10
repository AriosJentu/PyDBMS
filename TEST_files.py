import pytest
import binarydb
import exceptions as exc

database = binarydb.BinaryDataBase("testdbss.jpdb")
unexistdatabase = binarydb.BinaryDataBase("testdbsssss.jpdb")
database.create()


def test_connect_error():
	with pytest.raises(exc.DBConnectionException):
		database.connect()

	with pytest.raises(exc.DBFileException):
		unexistdatabase.connect()


def test_create_table_error():
	database.create_table("Hello", {"Kek": int, "Lol": str})
	with pytest.raises(exc.DBTableException):
		database.create_table("Hello", {"Kek": int})


def test_insert():
	for i in range(10):
		database["Hello"].insert([i], ["Kek"]) 
		database.Hello.insert([i+10], ["Kek"]) 
		database.insert_into("Hello", [i+20], ["Kek"]) 
		

def test_select():

	select1 = database.Hello.select("*")
	assert len(select1) == 30

	select = database.Hello.select("*", "id < 10")
	assert len(select) == 10

	select = database.Hello.select("*", "Kek%10 == 0 or Kek%5 == 1")
	assert len(select) == 9

	select2 = database.Hello.select(["Kek"])
	assert len(select1) == len(select2)

	assert len(select1.fields) > len(select2.fields)


def test_delete():

	database.Hello.delete_insecure("id >= 10")

	select = database.Hello.select("*")
	assert len(select) == 10


def test_secure_delete():

	bfsel = database.Hello.select("*")
	database.Hello.delete("id >= 3 and id <= 5")
	bsel = database.Hello.select("*")

	assert len(bfsel) == len(bsel)

	database.Hello.commit()
	asel = database.Hello.select("*")

	assert len(bsel) == len(asel)+3


def test_insert_error():
	with pytest.raises(exc.DBValueException):
		database.Hello.insert(["12"], ["Kek"]) 
		database.Hello.insert(["KEKOS"], ["Faaka"]) 


def test_insert_elements():

	elements = []
	cnt = len(database.Hello.select("*"))
	
	for i in range(8):
		row = database.Hello.insert([str(i)+"TEST"], ["Lol"])
		elements.append(row)

	sel = database.Hello.select("*", "id>={}".format(elements[0].id))

	for i in range(len(sel)):
		assert sel[i] == elements[i]


def test_remove_elements():

	sel = database.Hello.select("*", "id < 3 or id > 25")
	
	database.Hello.delete_insecure("id >= 3 and id <= 25")
	sels = database.Hello.select("*")

	for i in range(len(sel)):
		assert sel[i] == sels[i]


def test_push_to_removed():

	sel = database.Hello.select("*", removed=True)
	cnt = min(5, len(sel))
	for i in range(cnt):
		database.Hello.insert(["Kekos"+str(i)], ["Lol"])

	sels = database.Hello.select("*", removed=True)
	assert len(sels) == len(sel)-cnt


def test_copy_elements():
	
	sel = database.Hello.select("*")
	n = 10
	for i in range(n):
		database.Hello._copy_row(sel[-1].index)
	
	sel2 = database.Hello.select("*")
	
	assert len(sel2) == len(sel)+n


def test_update():

	database.Hello.insert([1488, "SASKA"])
	bsel = database.Hello.select("*", "id == 31 or id == 34")
	updt = database.Hello.update_insecure([2281488, "HELLOWORLD"], "*", "id == 31 or id == 34")
	asel = database.Hello.select("*", "id == 31 or id == 34")

	assert updt[0] != bsel[0] 
	assert updt[0] == asel[0] 

	assert updt[1] != bsel[1] 
	assert updt[1] == asel[1] 


def test_delete_row():
	
	bsel = database.Hello.select("*")
	database.Hello.delete_row(bsel[14])
	asel = database.Hello.select("*")

	assert len(bsel) == len(asel)+1


def test_update_cow():

	bsel = database.Hello.select("*")
	updt = database.Hello.update([1488228, "USETHEFORCELUKE"], "*", "id == 32 or id == 33")
	asel = database.Hello.select("*", upd_inc=True)

	assert len(bsel)+2 == len(asel)

	database.Hello.commit()	
	asel = database.Hello.select("*", upd_inc=True)

	assert len(bsel) == len(asel)



def test_clear_table():

	database.Hello.delete_insecure()
	assert len(database.Hello.select("*")) == 0

