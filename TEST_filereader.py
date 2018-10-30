from filereader import DataBase 				#Import DataBase

DataBase()										#Nothing happens

db = DataBase.open("database.jpdb")				#Creating database 
db._remove_file("test_unremovable.txt")			#File doesn't exist
db._remove_file("test_unrm_create.txt")			#File doesn't exist
db._create_file("test_unrm_create.txt")			#File created
db._remove_file("test_unrm_create.txt")			#File removed
db._create_file("not_only_meta.txt")			#File created
db._create_file("helloworld/testing/dir.txt")	#Directory doesn't exist
db._create_file("helloworld/testingdir.txt")	#Directory doesn't exist
db._create_directory("helloworld")				#Directory created
db._remove_directory("helloworld/test/kek")		#Directory doesn't exist
db._create_directory("helloworld/test/kek")		#Can't create directory
db._create_directory("helloworld/test")			#Directory created
db._create_file("helloworld/test/file.txt")		#File created
db._remove_directory("helloworld/test")			#Directory removed

print(db.get_file_list())						#Print list of files to commit
db.commit()										#Commit database to file
db._create_file("create_before_close.txt")		#File created
db.close()										#Close database