import random
import string
import sqlite3
import cherrypy
import hashlib
from helpers import *
import os, os.path
import MySQLdb

db = MySQLdb.connect(host="mysql.server", user="JamesonBruce", passwd="Hackrice2015", db="JamesonBruce$project")
cur = db.cursor()

from string import Template

cherrypy.config.update({'tools.sessions.on': True,
			   })

from string import Template


class StringGenerator(object):
	@cherrypy.expose
	def index(self, message = ""):
		result = Template(

			"""
<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title></title>
    <link rel="stylesheet" href="css/bootstrap.css">
    <link rel="stylesheet" href="css/login_style.css">
</head>
<body>
<h1>Connector</h1>
<div class="form-group">
    <form id="login_form" method="post" action="proposal_list_page.html">
        <fieldset>
            <h3>
                Email
            </h3>
            <input type="text" value="" class="form-control" name="email" style="width:220px;" required/>
            <h3>
                Password
            </h3>
            <input type="password" value="" class="form-control" name="password" style="width:220px;" required/>
            <div id="login-button">
                <p>
                    <button type="submit" class="btn btn-primary" id="login-button">Log in</button>
                </p>
            </div>

        </fieldset>
    </form>
</div>
<br><br>
    <fieldset id="signup">
        <p>
            Don't have an account?
        </p>
        <p>
            <a href="signup_page.html" class="btn btn-success">Sign up</a>
        </p>
    </fieldset>
<br>
    <div class="jumbotron">
        <h2>What is Connector?</h2>
        <p id="text">Connector is a social web app to connect you with people to do whatever you want to do. Want a group to go to the movies
        or to come party in your room? Propose the activity, and when enough people have seen the anonymous activity idea,
        we'll connect you guys via GroupMe automatically, and you can take it from there. What are you waiting for?</p>
        <p align="center"><a href="signup_page.html" id="#secondsignup" class="btn btn-success btn-lg">Sign up</a></p>
    </div>

</body>
</html>




			""")
		
		return str (result.substitute(tell_user = message))

	

	@cherrypy.expose
	def new_user_page(self, username="", password = ""):
		return """
			<!DOCTYPE html>
			<html>
			<head lang="en">
			    <meta charset="UTF-8">
			    <title></title>
			    <link rel="stylesheet" href="css/bootstrap.css">
			    <link rel="stylesheet" href="css/signup_style.css">
			</head>
			<body>
			<h2>Sign up for Connector</h2>
			<div class="form-group">
			    <form id="login_form" method="post" action="proposal_list_page.html">
			        <fieldset>
			            <h3>
			                Email
			            </h3>
			            <input type="text" value="" class="form-control" name="email" style="width:220px;" required/>
			            <h3>
			                Password
			            </h3>
			            <input type="password" value="" class="form-control" name="password" style="width:220px;" required/>
			            <h3>
			                Confirm Password
			            </h3>
			            <input type="text" value="" class="form-control" name="email" style="width:220px;" required/>
			            <h3>
			                Phone Number
			            </h3>
			            <input type="tel" value="" class="form-control" name="email" style="width:220px;" required/>
			            <div id="signup-button">
			                <p>
			                    <button type="submit" class="btn btn-primary" id="signup-button">Sign up</button>
			                </p>
			            </div>

			        </fieldset>
			    </form>
			</div>


			</body>
			</html>
			"""
		

	@cherrypy.expose
	def logged_in_page(self, username, password):
		cur.execute("SELECT username FROM user_info WHERE username=(%s)", [username])
		db_fetched = cur.fetchone()
		#print db_fetched
		if db_fetched == None:
			#failure to log in
			return """<meta http-equiv="refresh" content="1;url=index?message=no such user" />"""
		else:
			cur.execute("SELECT password FROM user_info WHERE username=(%s)", [username])
			db_fetched = cur.fetchone()[0]
			if(get_hash(password) == db_fetched):
				cherrypy.session['username'] = username
				#password is good
				return """<meta http-equiv="refresh" content="1;url=proposal_list_page" />"""
			else:
				return """<meta http-equiv="refresh" content="1;url=index?message=wrong password" />"""
	
	@cherrypy.expose
	def make_new_user(self, username="", password = "", confirm_password=""):
		if(username != "") and password == confirm_password:
			cur.execute('INSERT INTO user_info (username, password, phone) VALUES (%s, %s, %s)',[username, str(get_hash(password)), "phone"])
			db.commit()
			#print "put it in"
			return self.logged_in_page(username,password)
		else:
			return """<meta http-equiv="refresh" content="1;url=index?message=Please enter a username" />"""
		#return some_string
	


	


	@cherrypy.expose
	def proposal_list_page(self):
		result = """
		<!DOCTYPE html>
			<html>
			<head lang="en">
				<meta charset="UTF-8">
				<title>Partytown</title>
				<link rel="stylesheet" href="static/css/bootstrap.css">
				<link rel="stylesheet" href="static/css/proposal_page.css">
				<link rel="stylesheet" href="static/css/jquery-ui.css">


			</head>
			<body>
				<nav class="navbar navbar-default center" role="navigation">
					<div class="row">
					<div class="col-md-4">
					</div>
					<div class="col-md-4">
						<a href="propose_something_page" class="btn btn-success btn-lg btn-block">What do you want to do?</a>
					</div>
					<div class="col-md-4" align="right" id="logout">
						<a href="login_page.html" class="btn btn-info">Logout</a>
					</div>
				  </div>
				</nav>
			<div id="events">
			"""


		agreement_map = get_agreement_map()
		print( agreement_map)
		db_fetched = get_proposal_list()	
		if db_fetched != None:
			for item in db_fetched:
				'''
				result += "<h3>"+str(item[2])+"</h3>"
				result += "<p><b>Minimum size:</b> "+ str(item[3]) + "</p>"
				result += "<p><b>Maximum size:</b> " + str(item[4]) + "</p>"
				proposal_id = str(item[1])
				result += """<div class="success-button" align="center"><a href="agree_to_proposal?proposal_id="""+proposal_id+"""\" class="btn btn-success">"""
				username = cherrypy.session['username']
				if username in agreement_map and not int(proposal_id) in agreement_map[username]:
					result += "Let's do it"
				elif not username in agreement_map:
					result += "Let's do it"
				else:
					result += "I'm down."
					'''
				proposal_id = str(item[1])
				button_text = ""
				username = cherrypy.session['username']
				if username in agreement_map and not int(proposal_id) in agreement_map[username]:
					button_text = "Let's do it"
				elif not username in agreement_map:
					button_text = "Let's do it"
				else:
					button_text = "I'm down."
				result += """
						<h3>{}<div class="success-button" align="right" id="{}"><a class="btn btn-success btn-sm">{}</a></div></h3>
						<div >

							<p>{}</p>
							<p><b>Minimum size:</b> {}</p>
							<p><b>Maximum size:</b> {}</p>
							
						</div>
						""".format(str(item[0]), proposal_id, button_text, str(item[2]),str(item[3]),  str(item[4]))
				


		result += """</div>

			<script src="static/js/jquery.js"></script>
			<script src="static/js/jquery-ui.min.js"></script>
			<script src="static/js/proposal_script.js"></script>
			<script>
				$(".btn.btn-success.btn-sm").click(function(){
					var id_num = $(this).attr('id');
					jQuery.ajax("/agree_to_proposal?proposal_id="+id_num);

				});
			</script>
			</body>
			</html>"""
		return result

	@cherrypy.expose
	def agree_to_proposal(self,proposal_id=""):
		cur.execute('INSERT INTO agrees (proposal_id, username) VALUES (%s, %s)', [str(proposal_id), cherry.py.session['username']])
		return """<meta http-equiv="refresh" content=1;url=proposal_list_page" />"""



	@cherrypy.expose
	def propose_something_page(self):
		result = """
		<!DOCTYPE html>
<html>
<head lang="en">
	<meta charset="UTF-8">
	<title>Propose an activity</title>
	<link rel="stylesheet" href="css/bootstrap.css">
	<link rel="stylesheet" href="css/activity.css">
</head>
<body>
<h2>Propose something</h2>
<div class="form-group">
	<form id="activity_form" method="post" action="proposal_db_insert">
		<fieldset>
			<h3>
				Proposal name
			</h3>
			<input type="text" value="" name="proposal_name" class="form-control" style="width:300px;" required>
			<h3>
				Proposal description
			</h3>
			<textarea name="proposal_description" form="activity_form" class="form-control" style="width:300px" rows="4">
			</textarea>
			<h3>
				Minimum number of people
			</h3>
			<input type="number" value="2" name="min_num_people" class="form-control" style="width:300px;" min="2" max="20">
			<h3>
				Maximum number of people
			</h3>
			<input type="number" value="2" name="max_num_people" class="form-control" style="width:300px;" min="2" max="100">
			<br>
			<p><button type="submit" class="btn btn-primary" id="proposal-button">Propose!</button></p>
		</fieldset>
	</form>
</div>

</body>
</html>
"""

	@cherrypy.expose
	def proposal_db_insert(self, proposal_name="", proposal_description="", min_num_people="", max_num_people=""):
		cur.execute('INSERT INTO proposals (proposal_id, proposal_name, description, min_people, max_people) VALUES (%s, %s, %s, %s, %s)', [get_num_proposals()+1, proposal_name, proposal_description, int(min_num_people), int(max_num_people)])
		db.commit()
		return """<meta http-equiv="refresh" content="1;url=proposal_list_page" />"""


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
	print ("exit")
	#delete_databases()

def setup_database():
	"""
	Create the `username_password_db` table in the database
	on server startup
	"""

	print("startup")
	'''
	with sqlite3.connect(USER_DB_STRING) as con:
		con.execute("CREATE TABLE username_password_db (username, password)")
	with sqlite3.connect(PROPOSALS_DB_STRING) as con:
		con.execute("CREATE TABLE proposals_db (proposal_id, proposal_name, description, min_people, max_people)")
	with sqlite3.connect(AGREES_DB_STRING) as con:
		con.execute("CREATE TABLE agrees_db (proposal_id, username)")
		'''




if __name__ == '__main__':
	conf = {
		 '/': {
			 'tools.sessions.on': True,
			 'tools.staticdir.root': os.path.abspath(os.getcwd())
		 },
		 '/static': {
			 'tools.staticdir.on': True,
			 'tools.staticdir.dir': './public'
		 }
	}

	cherrypy.engine.subscribe('start', setup_database)
	cherrypy.engine.subscribe('stop', cleanup_database)
	cherrypy.quickstart(StringGenerator(), '/', conf)



