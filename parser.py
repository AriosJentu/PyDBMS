from pyparsing import Word, alphas, ZeroOrMore, Optional

class Parser:

	@staticmethod
	def create_basic(sqlstring):

		result = {
			"table": {
				"name": "",
				"fields": []
			},
		}

		#-----------------

		langCommands = ["create"]
		langWords = ["table"]
		bracketOn = False

		word = ZeroOrMore(Word(alphas + '('  + ')').\
			ignore(",").ignore('"').ignore("'"))


		request = word 

		parseRequest = {} #список запросов на каждый запрос свой дикт(TODO)

		list_ = request.parseString(sqlstring)
		#print(list_)

		values = []

		for i in range(len(list_)):	

			command = " "
			expName = " "


			if(list_[i] == "("):
				bracketOn = True
				continue
			
			if(list_[i] == ")"):
				bracketOn = False
				continue		

			if(list_[i] in langWords):

				command = list_[i]
				#print(command)

			if ( 
					list_[i] not in langWords and 
					list_[i] not in langCommands and 
					not bracketOn
			):
				expName = list_[i]

				if expName != " ":
					result["table"]["name"] = expName
				
				#print(expName)

			if ( 
					list_[i] not in langWords and 
					list_[i] not in langCommands and 
					bracketOn
			):

				values.append(list_[i])

		result["table"]["fields"] = values
		
		return result

	@staticmethod
	def show_create_basic(sqlstring):
		
		result = {
			"show": {
				"name": ""
			},
		}
		
		langCommands = ["show"]
		langWords = ["table"]
		bracketOn = False

		word = ZeroOrMore(Word(alphas).ignore(",").ignore('"').ignore("'"))


		request = word 

		parseRequest = {}

		list_ = request.parseString(sqlstring)
		for i in range(len(list_)):
			
			if (list_[i] in langCommands):

				command = list_[i]

				#print(command)

			if ( 
					list_[i] not in langWords and 
					list_[i] not in langCommands 
			):

				expName = list_[i]

				if expName != " ":
					result["show"]["name"] = expName

		return result

	@staticmethod
	def select_basic(sqlstring):


		result = {
			"select": {
				"table": "",
				"values": []
			},
		}	

		langCommands = ["select"]
		langWords = ["from"]

		request = ZeroOrMore(Word(alphas).ignore(",").ignore('"').ignore("'"))
		list_ = request.parseString(sqlstring)
		

		command =""
		tableName = list_[len(list_)-1]
		values = []

		for i in range(len(list_) - 1):

			if (
					list_[i] not in langWords and 
					list_[i] not in langCommands
			):

				values.append(list_[i])	

		result["select"]["table"] = tableName
		result["select"]["values"] = values

		return result

	@staticmethod
	def insert_basic(sqlstring):


		result = {
			"insert": {
				"table": "",
				"values": []
			},
		}	

		langCommands = ["insert"]
		langWords = ["into", "values"]

		
		valuesOn = False
		upComma = Optional("'")

		request = ZeroOrMore(Word(alphas).ignore(",").\
			ignore('"').ignore("(").ignore(")").ignore("'"))

		list_ = request.parseString(sqlstring)
		#print(list_)

		values = []
		command = " "
		expName = " "

		for i in range(len(list_)):	

			
			if(list_[i] == "values"):
				valuesOn = True
			

			if(list_[i] in langCommands):

				command = list_[i]
		
				#print(command)

			if ( 
					list_[i] not in langWords and 
					list_[i] not in langCommands and 
					not valuesOn 
			):

				expName = list_[i]
				
				result["insert"]["table"] = expName
				#print(expName)

			if ( 
					list_[i] not in langWords and 
					list_[i] not in langCommands and 
					valuesOn
			):
		
				values.append(list_[i])

		result["insert"]["values"] = values
		
		return result

	


#print(Parser.create_basic("create table 'KEKOS' ('id', 'name', \"HUI\")"))
#print(Parser.show_create_basic("show create table 'KEKOS'"))
#print(Parser.select_basic("select a, b from test"))
#print(Parser.insert_basic("insert into test values (a, 'b')"))