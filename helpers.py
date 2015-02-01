import hashlib
import sqlite3







USER_DB_STRING = "users.db"
PROPOSALS_DB_STRING = "proposals.db"
AGREES_DB_STRING = "agrees.db"


def get_proposal_list():
	
	conn = sqlite3.connect(PROPOSALS_DB_STRING)
	cursor=conn.cursor()
	cursor.execute("SELECT proposal_name, proposal_id, description, min_people, max_people FROM proposals_db")
	db_fetched = cursor.fetchall()	
	return db_fetched

def get_num_proposals():
	return len(get_proposal_list())

def get_agreement_map():
	"""
	returns a mapping of user -> set of events she agrees to
	"""
	conn = sqlite3.connect(AGREES_DB_STRING)
	cursor=conn.cursor()
	cursor.execute("SELECT username, proposal_id FROM agrees_db")
	db_fetched = cursor.fetchall()	
	result = {}
	for item in db_fetched:
		try: #try is necesary because while playing with DBs we have introduced some non integers where integet strings should be
			if not item[0] in result:
				result[item[0]] = {int(item[1])}
			else:
				result[item[0]].add(int(item[1]))
		except:
			pass
	return result




def get_num_rows(dbFile):
	connection = sqlite3.connect(dbFile)
	cursor = connection.cursor()
	
	#Print("TableName\tColumns\tRows\tCells")
 
	totalTables = 0
	totalColumns = 0
	totalRows = 0
	totalCells = 0
	
	# Get List of Tables:	  
	tableListQuery = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY Name"
	cursor.execute(tableListQuery)
	tables = map(lambda t: t[0], cursor.fetchall())
	
	for table in tables:
	
		
			
		columnsQuery = "PRAGMA table_info(%s)" % table
		cursor.execute(columnsQuery)
		numberOfColumns = len(cursor.fetchall())
		
		rowsQuery = "SELECT Count() FROM %s" % table
		cursor.execute(rowsQuery)
		numberOfRows = cursor.fetchone()[0]
		
		numberOfCells = numberOfColumns*numberOfRows
		
		#Print("%s\t%d\t%d\t%d" % (table, numberOfColumns, numberOfRows, numberOfCells))
		
		totalTables += 1
		totalColumns += numberOfColumns
		totalRows += numberOfRows
		totalCells += numberOfCells
 
	#Print( "" )
	#Print( "Number of Tables:\t%d" % totalTables )
	#Print( "Total Number of Columns:\t%d" % totalColumns )
	#Print( "Total Number of Rows:\t%d" % totalRows )
	#Print( "Total Number of Cells:\t%d" % totalCells )
		
	cursor.close()
	connection.close()  
	return totalRows 
 

def get_hash(password):
	password = password.encode('utf-8')
	return hashlib.sha1(password).hexdigest()

def get_n_selector(n, name):
	result = "<select name="+name+">"
	for i in range(2,n+1):
		result += "<option value="+str(i)+">"+str(i)+"</option>"
	result +="	</select>"
	return result