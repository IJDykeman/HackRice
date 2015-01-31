import random
import string
import sqlite3
import cherrypy
import hashlib
from helpers import *

USER_DB_STRING = "users.db"
PROPOSALS_DB_STRING = "proposals.db"
AGREES_DB_STRING = "agrees.db"
from string import Template


class StringGenerator(object):
	@cherrypy.expose
	def index(self, message = "Welcome"):
		result = Template("""<html>
			<head></head>
			<body>
			$tell_user
			<form method="post" action="logged_in_page">
			  <input type="text" value="" name="username" />
			  <input type="text" value="" name="password" />
				  <button type="submit">Sign in</button>
			</form>
			<a href="new_user_page">sign up to start making cards</a>
		  </body>
		</html>""")
		
		return str (result.substitute(tell_user = message))

	

	@cherrypy.expose
	def new_user_page(self, username="", password = ""):
		return """<html>
			<head></head>
			<body>
			<form method="post" action="make_new_user">
			  <input type="text" value="" name="username" />
			  <input type="text" value="" name="password" />
				  <button type="submit">Sign up</button>
			</form>
			<a href="index">log in</a>
		  </body>
		</html>"""



	@cherrypy.expose
	def logged_in_page(self, username, password):
		conn = sqlite3.connect(USER_DB_STRING)
		cursor=conn.cursor()
		cursor.execute("SELECT username FROM username_password_db WHERE username=?",
					   [username])
		db_fetched = cursor.fetchone()
		#print db_fetched
		if db_fetched == None:
			#failure to log in
			return """<meta http-equiv="refresh" content="1;url=index?message=no such user" />"""
		else:
			cursor=conn.cursor()
			cursor.execute("SELECT password FROM username_password_db WHERE username=?",
						   [username])
			db_fetched = cursor.fetchone()[0]
			if(get_hash(password) == db_fetched):
				cherrypy.session['username'] = username
				#password is good
				return """<meta http-equiv="refresh" content="1;url=proposal_list_page" />"""
			else:
				return """<meta http-equiv="refresh" content="1;url=index?message=wrong password" />"""
	
	@cherrypy.expose
	def make_new_user(self, username="", password = ""):
		if(username != ""):
			with sqlite3.connect(USER_DB_STRING) as conn:
				conn.execute("INSERT INTO username_password_db VALUES (?, ?)",
					[username, get_hash(password)])
			#print "put it in"
			return self.logged_in_page(username,password)
		else:
			return """<meta http-equiv="refresh" content="1;url=index?message=Please enter a username" />"""
		#return some_string
	

	def get_proposal_list(self):
		
		conn = sqlite3.connect(PROPOSALS_DB_STRING)
		cursor=conn.cursor()
		cursor.execute("SELECT proposal_name, proposal_id, description, min_people, max_people FROM proposals_db")
		db_fetched = cursor.fetchall()	
		return db_fetched
	

	def get_num_proposals(self):
		return len(self.get_proposal_list())


	@cherrypy.expose
	def proposal_list_page(self):
		result = "<html><head></head><body>"+cherrypy.session['username']+"'s' proposal list: "
		result += """<br><a href="propose_something_page">Propose something!</a>"""
		db_fetched = self.get_proposal_list()	
		if db_fetched != None:
			result += "<br>There are currently " + str(len(db_fetched))+ " proposals<br>"
			for item in db_fetched:


				result += """<a href = "agree_to_proposal?proposal_id=\""""+str(item[1])+""">Click to Attend</a>"""
				result +=str(item[0]) + "<br>---"+str(item[2])+"("+str(item[3])+"-"+str(item[4])+" people)" + "<br>"
		
		result += "</body></html>"
		return result

	@cherrypy.expose
	def agree_to_proposal(self,proposal_id=""):
		with sqlite3.connect(AGREES_DB_STRING) as conn:
			conn.execute("INSERT INTO agrees_db VALUES (?, ?)",
				[username, proposal_id])
		return """<meta http-equiv="refresh" content="1;url=proposal_list_page" />"""

	@cherrypy.expose
	def propose_something_page(self):
		result = "<html><head></head><body>"
		result += """
		<form method="post" action="proposal_db_insert">
			  Proposal name<input type="text" value="" name="proposal_name" /><br>
			  Proposal description<input type="text" value="" name="proposal_description" />
				  
				  <br><br>
				  Minimum number of people
				  """
		result += get_n_selector(20, "max_num_people")
		result += "Maximum number of people"
		result += get_n_selector(50,"min_num_people")
		result += "<button type=\"submit\">Propose!</button></form>"
		result += "</body></html>"
		return result

	@cherrypy.expose
	def proposal_db_insert(self, proposal_name="", proposal_description="", min_num_people="", max_num_people=""):
		with sqlite3.connect(PROPOSALS_DB_STRING) as c:
			c.execute("INSERT INTO proposals_db VALUES (?, ?, ?, ?, ?)",
				[self.get_num_proposals()+1, proposal_name, proposal_description, int(min_num_people), int(max_num_people)])
		return """<meta http-equiv="refresh" content="1;url=proposal_list_page" />"""

	@cherrypy.expose
	def edit_card(self, proposal_id = ""):
		print("in edit card")
		conn = sqlite3.connect(PROPOSALS_DB_STRING)
		cursor=conn.cursor()
		cursor.execute("SELECT college_name, description FROM proposals_db WHERE proposal_id=? and username=?",
				[ int(proposal_id), cherrypy.session['username']])
		db_fetched = cursor.fetchone()	
		result = Template("""<html>
			<head></head>
			<body>
			<form method="post" action="save_card_form?proposal_id=$cardid">
			  <input type="text" value="$school_name" name="school_name" />
			  <input type="text" value="$description" name="description" />
				  <button type="submit">Save</button>
			</form>
			<br>
			<a href="proposal_list_page">Back to card list</a>
		  </body>
		</html>""")
		
		return str (result.substitute(school_name = db_fetched[0], description = db_fetched[1], cardid = proposal_id))

	@cherrypy.expose
	def save_card_form(self, school_name="", proposal_description="", proposal_id=""):
		with sqlite3.connect(PROPOSALS_DB_STRING) as c:
			c.execute("UPDATE proposals_db SET college_name=?, description=? WHERE proposal_id=? and username=?",
				[school_name, description, int(proposal_id), cherrypy.session['username']  ])
		return "<meta http-equiv=\"refresh\" content=\"1;url=edit_card?proposal_id="+proposal_id + "\" />"
def delete_databases():
	with sqlite3.connect(USER_DB_STRING) as con:
		con.execute("DROP TABLE username_password_db")
	with sqlite3.connect(PROPOSALS_DB_STRING) as con:
		con.execute("DROP TABLE proposals_db")
	with sqlite3.connect(AGREES_DB_STRING) as con:
		con.execute("DROP TABLE agrees_db")

def cleanup_database():
	"""
	Destroy the `username_password_db` table from the database
	on server shutdown.
	"""
	delete_databases()

def setup_database():
	"""
	Create the `username_password_db` table in the database
	on server startup
	"""

	print("startup")
	with sqlite3.connect(USER_DB_STRING) as con:
		con.execute("CREATE TABLE username_password_db (username, password)")
	with sqlite3.connect(PROPOSALS_DB_STRING) as con:
		con.execute("CREATE TABLE proposals_db (proposal_id, proposal_name, description, min_people, max_people)")
	with sqlite3.connect(AGREES_DB_STRING) as con:
		con.execute("CREATE TABLE agrees_db (proposal_id, username)")


if __name__ == '__main__':
	conf = {
		'/': {
			'tools.sessions.on': True
		}
	}
	cherrypy.engine.subscribe('start', setup_database)
	cherrypy.engine.subscribe('stop', cleanup_database)
	cherrypy.quickstart(StringGenerator(), '/', conf)



