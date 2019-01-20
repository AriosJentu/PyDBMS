import pytest
import logic
import classes
import exceptions as exc
import threading
import time

database = logic.DataBase("testdbss.jpdb")
unexistdatabase = logic.DataBase("testdbsssss.jpdb")
database.create(recreate=True)


def test_connect_error():	#1
	with pytest.raises(exc.DBConnectionException):
		database.connect()

	with pytest.raises(exc.DBFileException):
		unexistdatabase.connect()


def test_create_table_error():	#2
	database.create_table("Hello", {"Kek": int, "Lol": str})
	with pytest.raises(exc.DBTableException):
		database.create_table("Hello", {"Kek": int})


def test_insert():	#3
	for i in range(10):
		database["Hello"].insert([i], ["Kek"]) 
		database.Hello.insert([i+10], ["Kek"]) 
		database.insert_into("Hello", [i+20], ["Kek"]) 
		

def test_select():	#4

	select1 = database.Hello.select("*")
	assert len(select1) == 30

	select = database.Hello.select("*", "id < 10")
	assert len(select) == 10

	select = database.Hello.select("*", "Kek%10 == 0 or Kek%5 == 1")
	assert len(select) == 9

	select2 = database.Hello.select(["Kek"])
	assert len(select1) == len(select2)

	assert len(select1.fields) > len(select2.fields)


def test_delete():	#5

	database.Hello.delete_insecure("id >= 10")

	select = database.Hello.select("*")
	assert len(select) == 10


def test_secure_delete():	#6

	bfsel = database.Hello.select("*")
	database.Hello.delete("id >= 3 and id <= 5")
	bsel = database.Hello.select("*")

	assert len(bfsel) == len(bsel)

	database.Hello.commit()
	asel = database.Hello.select("*")

	assert len(bsel) == len(asel)+3


def test_insert_error():	#7
	with pytest.raises(exc.DBValueException):
		database.Hello.insert(["12"], ["Kek"]) 
		database.Hello.insert(["KEKOS"], ["Faaka"]) 


def test_insert_elements():	#8

	elements = []
	cnt = len(database.Hello.select("*"))
	
	for i in range(8):
		row = database.Hello.insert([str(i)+"TEST"], ["Lol"])
		elements.append(row)

	sel = database.Hello.select("*", "id>={}".format(elements[0].id))

	for i in range(len(sel)):
		assert sel[i] == elements[i]


def test_remove_elements():	#9

	sel = database.Hello.select("*", "id < 3 or id > 25")
	
	database.Hello.delete_insecure("id >= 3 and id <= 25")
	sels = database.Hello.select("*")

	for i in range(len(sel)):
		assert sel[i] == sels[i]


def test_push_to_removed():	#10

	sel = database.Hello.select("*", removed=True)
	cnt = min(5, len(sel))
	for i in range(cnt):
		database.Hello.insert(["Kekos"+str(i)], ["Lol"])

	sels = database.Hello.select("*", removed=True)
	assert len(sels) == len(sel)-cnt


def test_copy_elements():	#11
	
	sel = database.Hello.select("*")
	n = 10
	for i in range(n):
		database.Hello._copy_row(sel[-1].index)
	
	sel2 = database.Hello.select("*")
	
	assert len(sel2) == len(sel)+n


def test_update():	#12

	database.Hello.insert([1488, "SASKA"])
	bsel = database.Hello.select("*", "id == 31 or id == 34")
	updt = database.Hello.update_insecure([2281488, "HELLOWORLD"], "*", "id == 31 or id == 34")
	asel = database.Hello.select("*", "id == 31 or id == 34")

	assert updt[0] != bsel[0] 
	assert updt[0] == asel[0] 

	assert updt[1] != bsel[1] 
	assert updt[1] == asel[1] 


def test_delete_row():	#13
	
	bsel = database.Hello.select("*")
	database.Hello.delete_row(bsel[14])
	asel = database.Hello.select("*")

	assert len(bsel) == len(asel)+1


def test_update_cow():	#14
	
	bsel = database.Hello.select("*")
	updt = database.Hello.update([1488228, "USETHEFORCELUKE"], "*", "id == 32 or id == 33")
	asel = database.Hello.select("*", upd_inc=True)

	assert len(bsel)+2 == len(asel)

	database.Hello.commit()	
	asel = database.Hello.select("*", upd_inc=True)

	assert len(bsel) == len(asel)


def test_exec_select():	#15

	select1 = database.exec("SELECT Kek FROM Hello")
	select2 = database.select_from("Hello", "Kek")
	assert len(select1) == len(select2)


def test_exec_create():	#16

	table = database.exec(
		"CREATE TABLE HelloWorld ('Test1' int, 'Test2' string, 'Test3' bool)"
	)

	for i in range(3):
		assert database.HelloWorld.fields[i] == "Test"+str(i+1)
		assert database.HelloWorld.types[i] == [int, str, bool][i]
		assert database.HelloWorld.types[i] != [bool, int, str][i] 

	for i in range(10):
		database.HelloWorld.insert([i+1479, "Kek", True if i%2 == 1 else False])
	

def test_exec_show_create():	#17

	res1 = database.exec("SHOW CREATE TABLE HelloWorld")
	res2 = database.HelloWorld.show_create()
	assert res1 == res2


def test_exec_delete():	#18

	sel1 = database.exec("SELECT Test1 FROM HelloWorld")
	database.exec("DELETE FROM HelloWorld WHERE Test1 == 1487")
	database.HelloWorld.commit()
	
	sel2 = database.exec("SELECT Test1 FROM HelloWorld")
	assert len(sel1) == len(sel2)+1


def test_select_update_parallel():	#19

	select_main = database.Hello.select("*", "id == 2")

	def func1():
		s1 = database.Hello.select("*", "id == 2")
		assert s1[0] == select_main[0]

	def func2():

		#BEFORE
		s2 = database.Hello.select("*", "id == 2")
		assert s2[0] == select_main[0]

		database.Hello.update([2281488, "SOSIPISOS"], "*", "id == 2")
		database.Hello.commit()

		#AFTER
		s2 = database.Hello.select("*", "id == 2")
		assert s2[0] != select_main[0]


	thread1 = threading.Thread(target=func1)
	thread2 = threading.Thread(target=func2)

	thread1.start()
	thread2.start()

	thread1.join()
	thread2.join()

	s3 = database.Hello.select("*", "id == 2")
	assert s3[0] != select_main[0]


def test_update_parallel():	#20

	def func1():
		database.Hello.update([2281488, "SOSIPISOS"], "*", "id == 2")

	def func2():
		database.Hello.update([2281489, "SOSIPISOS"], "*", "id == 2")


	thread1 = threading.Thread(target=func1)
	thread2 = threading.Thread(target=func2)

	thread1.start()
	thread2.start()

	thread1.join()
	thread2.join()

	s = database.Hello.select("*", "id == 2")
	assert len(s) == 1


def test_update_parallel_10_times():	#21

	def funcn(n):
		def func():
			database.Hello.update([2281480+n, "SOSIPISOS"], "*", "id == 2")
		return func

	threads = []
	for i in range(10):
		func = funcn(i)
		threads.append(threading.Thread(target=func))
		threads[-1].start()

	for thread in threads:
		thread.join()

	s = database.Hello.select("*", "id == 2")
	assert len(s) == 1
	assert s[0].values.Kek == 2281480+9


def test_update_parallel_200_times():	#22

	def funcn(n):
		def func():
			database.Hello.update([2281480+n, "SOSIPISOS"], "*", "id == 2")
		return func

	threads = []
	for i in range(200):
		func = funcn(i)
		threads.append(threading.Thread(target=func))
		threads[-1].start()

	for thread in threads:
		thread.join()

	s = database.Hello.select("*", "id == 2")
	assert len(s) == 1
	assert s[0].values.Kek == 2281480+199


def test_clear_table():	#24

	database.Hello.delete_insecure()
	assert len(database.Hello.select("*")) == 0


def test_dohuya_inserts():	#23
	
	database.create_table("Kekosik", {"C1": int, "C2": int})

	def func1():
		for i in range(10):
			database.Kekosik.insert([1488, 228])

	def func2():
		for i in range(10):
			database.Kekosik.insert([1489, 228])

	thread1 = threading.Thread(target=func1)
	thread2 = threading.Thread(target=func2)

	thread1.start()
	thread2.start()

	thread1.join()
	thread2.join()

	database.Kekosik.delete_insecure()
	assert len(database.Kekosik.select("*")) == len(database.Hello.select("*"))
