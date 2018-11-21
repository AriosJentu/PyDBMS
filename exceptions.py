#Exception class
class DBException(Exception):

	Exist = "{} '{}' already exist."
	DoesntExist = "{} '{}' doesn't exist."

	Exceptions = {

		0:	"Data Base Error!",
		1:	Exist.format("File", "{}"),
		2:	DoesntExist.format("File", "{}"),
		3:	Exist.format("Table", "{}"),
		4:	DoesntExist.format("Table", "{}"),
		5:	"Wrong Data Base Signature.",
		6:	"Data Base isn't connected.",
		7:	"Already too much tables inside.",
		8:	"Count of fields and count of types are different.",
		9:	"Too much Table's Fields.",
		10:	"Count of pages for table '{}' too much.",
		11:	DoesntExist.format("Field Type", "{}"),
		12:	"Incorrect values count for {}: Need '{}', Got: '{}'.",
		13:	"Value with index '{}' need to be '{}', but got '{}'.",
		14:	"Data Base already connected.",
		15:	"Count of values and fields are different.",
	}
	
	def __init__(self, message, *args):
		
		ex = DBException.Exceptions
		if type(message) == int and 0 <= message < len(ex):
			super().__init__(ex[message].format(*args))
		else:
			super().__init__(message.format(*args))


class DBConnectionException(DBException):
	def __init__(self, i, *args):
		
		indexes = [
			"Data Base isn't connected.",
			"Data Base already connected.",
		]
		
		super().__init__(indexes[i], *args)

class DBFileException(DBException):
	def __init__(self, i, *args):
		indexes = [
			DBException.Exist.format("File", "{}"),
			DBException.DoesntExist.format("File", "{}"),
			"Already too much tables inside.",
			"Wrong Data Base Signature.",
		]
		super().__init__(indexes[i], *args)

class DBTableException(DBException):
	def __init__(self, i, *args):
		
		indexes = [
			DBException.Exist.format("Table", "{}"),
			DBException.DoesntExist.format("Table", "{}"),
			"Too much Table's Fields.",
			DBException.DoesntExist.format("Field Type", "{}"),
		]

		super().__init__(indexes[i], *args)

class DBPageException(DBException):
	def __init__(self, i, *args):
		indexes = [
			"Count of pages for table '{}' too much.",
		]
		super().__init__(indexes[i], *args)

class DBValueException(DBException):
	def __init__(self, i, *args):

		indexes = [
			"Count of fields and count of types are different.",
			"Incorrect values count for {}: Need '{}', Got: '{}'.",
			"Value with index '{}' need to be '{}', but got '{}'.",
			"Count of values and fields are different.",
		]

		super().__init__(indexes[i], *args)
