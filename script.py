import random
import string
import sqlite3
import cherrypy
import hashlib
from helpers import *

USER_DB_STRING = "users.db"
PROPOSALS_DB_STRING = "proposals.db"
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
				return """<meta http-equiv="refresh" content="1;url=college_list" />"""
			else:
				return """<meta http-equiv="refresh" content="1;url=index?message=wrong password" />"""
	
	@cherrypy.expose
	def make_new_user(self, username="", password = ""):
		if(username != ""):
			with sqlite3.connect(USER_DB_STRING) as c:
				c.execute("INSERT INTO username_password_db VALUES (?, ?)",
					[username, get_hash(password)])
			#print "put it in"
			return self.logged_in_page(username,password)
		else:
			return """<meta http-equiv="refresh" content="1;url=index?message=please enter a username" />"""
		#return some_string
	

	def get_college_card_list(self):
		
		conn = sqlite3.connect(PROPOSALS_DB_STRING)
		cursor=conn.cursor()
		cursor.execute("SELECT college_name, proposal_id, description FROM proposals_db WHERE username=?",
				[cherrypy.session['username'] ])
		db_fetched = cursor.fetchall()	
		return db_fetched
	

	def get_num_college_cards(self):
		return len(self.get_college_card_list())


	@cherrypy.expose
	def college_list(self):
		result = "<html><head></head><body>"+cherrypy.session['username']+"'s' college list: <br>"
		db_fetched = self.get_college_card_list()	
		if db_fetched != None:
			result += "<br>you have entered " + str(len(db_fetched))+ " schools<br>"
			for item in db_fetched:
				result += "<a href=\"edit_card?proposal_id="+str(int(item[1])) + "\">"+str(item[0]) + "</a><br>"
		result += """<br><a href="new_card">add a college card!</a>"""
		result += "</body></html>"
		return result

	@cherrypy.expose
	def new_card(self):
		with sqlite3.connect(PROPOSALS_DB_STRING) as c:
			c.execute("INSERT INTO proposals_db VALUES (?, ?, ?, ?)",
				[self.get_num_college_cards()+1, cherrypy.session['username'],  "new school", "this is a description"])
		return """<meta http-equiv="refresh" content="1;url=college_list" />"""

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
			<a href="college_list">Back to card list</a>
		  </body>
		</html>""")
		
		return str (result.substitute(school_name = db_fetched[0], description = db_fetched[1], cardid = proposal_id))

	@cherrypy.expose
	def save_card_form(self, school_name="", description="", proposal_id=""):
		with sqlite3.connect(PROPOSALS_DB_STRING) as c:
			c.execute("UPDATE proposals_db SET college_name=?, description=? WHERE proposal_id=? and username=?",
				[school_name, description, int(proposal_id), cherrypy.session['username']  ])
		return "<meta http-equiv=\"refresh\" content=\"1;url=edit_card?proposal_id="+proposal_id + "\" />"

def setup_database():
	"""
	Create the `username_password_db` table in the database
	on server startup
	"""
	print("startup")
	with sqlite3.connect(USER_DB_STRING) as con:
		con.execute("CREATE TABLE username_password_db (username, password)")
	with sqlite3.connect(PROPOSALS_DB_STRING) as con:
		con.execute("CREATE TABLE proposals_db (proposal_id, name, people, description, min_people, max_people)")

def cleanup_database():
	"""
	Destroy the `username_password_db` table from the database
	on server shutdown.
	"""
	with sqlite3.connect(USER_DB_STRING) as con:
		con.execute("DROP TABLE username_password_db")
	with sqlite3.connect(PROPOSALS_DB_STRING) as con:
		con.execute("DROP TABLE proposals_db")

if __name__ == '__main__':
	conf = {
		'/': {
			'tools.sessions.on': True
		}
	}
	cherrypy.engine.subscribe('start', setup_database)
	cherrypy.engine.subscribe('stop', cleanup_database)
	cherrypy.quickstart(StringGenerator(), '/', conf)
	setup_database()


