from pyparsing import Word, alphas, ZeroOrMore

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

		word = ZeroOrMore(Word(alphas + '('  + ')').ignore(",").ignore('"').ignore("'"))


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

			if( ( not(list_[i] in langWords) and not(list_[i] in langCommands) and not(bracketOn)) ):
				expName = list_[i]
				if expName != " ":
					result["table"]["name"] = expName
				#print(expName)

			if( ( not(list_[i] in langWords) and not(list_[i] in langCommands) and (bracketOn)) ):
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
		#-----------------------------
		#-- TODO: show create table --
		#-----------------------------

		return result

Parser.create_basic("create table 'KEKOS' ('id', 'name', \"HUI\")")
Parser.show_create_basic("show create table 'KEKOS'")


