#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response,session,flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "yq2247"
DB_PASSWORD = "694574bd"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)





# Here we create a test table and insert some values in it
#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM Restaurant LIMIT 5")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print name
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  g.conn.execute(text(cmd), name1 = name, name2 = name);
  return redirect('/')



################################################################################
@app.route('/login', methods=['post'])
def login():
    pw = request.form['password']
    un = request.form['username']

    #Search CUstomer
    cmd = 'SELECT * FROM Customer WHERE Email = (:un1) AND Password = (:pw1)';
    cursor = g.conn.execute(text(cmd),un1 = un, pw1 =pw)
    record = []
    for result in cursor:
        record.append(result[0])
    cursor.close()

    #Search Manager
    cmd1 = 'SELECT * FROM Manager WHERE Email = (:un2) AND Password = (:pw2)';
    cursor1 = g.conn.execute(text(cmd1),un2 = un, pw2 =pw)
    record1 = []
    for result in cursor1:
        record1.append(result[0])
    cursor1.close()

    if record:
        if request.form['attribute'] == 'customer':
            #session['logged_in'] = True

            #Search cuisine type
            cmd1 = 'SELECT distinct Cuisine_Type FROM CuisineType'
            cursor1 = g.conn.execute(text(cmd1));
            cui = []
            for result in cursor1:
                cui.append(result[0])
                cursor.close()
            print cui

            context2 = dict(cui = cui)
            flash('Login scuuess','ok')
            return render_template("LogForCustomer.html",**context2)
        else:
            flash('Wrong username or password','no')
            return render_template("index.html")
    if record1:
        if request.form['attribute'] == 'manager':
            #session['logged_in'] = True
            flash('Login scuuess','okmanager')
            return render_template("LogForManager.html")
        else:
            flash('Wrong username or password','no')
            return render_template("index.html")
    else:
        flash('Wrong username or password','no')
        return render_template("index.html")


#######################################################################
#Sign Up
@app.route('/signup', methods=['post'])
def signup():
    return render_template("signup.html")

#Sign Up Judgement
@app.route('/signupsuccess', methods=['post'])
def signupsuccess():
    password = request.form['password'];
    username = request.form['username'];
    name = request.form['name'];
    if not name or not username or not password:
        flash('Please Input all boxes','signupfail')
        return render_template("signup.html")

    print password, username, name;

    #Find cid
    cmd = "SELECT MAX(CID) FROM Customer"
    cursor = g.conn.execute(text(cmd));
    results = []
    for result in cursor:
        results.append(result[0])
    cursor.close()
    print results
    CID = int(results[0]) +1


    #Insert User
    cmd = 'INSERT INTO Customer VALUES (:CID,:Email,:Password,:Name)'
    cursor = g.conn.execute(text(cmd),CID = CID,Email = username, Password = password, Name = name);
    cursor.close()
    cmd = "SELECT MAX(CID) FROM Customer"
    cursor = g.conn.execute(text(cmd));
    results = []
    for result in cursor:
        results.append(result[0])
    cursor.close()
    print results
    flash('Welcome!','siguupsuccess')
    return render_template("index.html")



#Locate the nearest 5 restaurants
@app.route('/locate', methods=['POST'])
def locate():
    lo = request.form['Longitude']
    la = request.form['Latitude']
    cmd = 'SELECT R.name FROM  Restaurant R,Address A WHERE R.LongAddress = A.LongAddress ORDER BY (A.Longitude - (:lo1))^2 + (A.Latitude-(:la1))^2 LIMIT 5';
    cursor = g.conn.execute(text(cmd),lo1 = lo,la1 = la);
    Name = []
    for result in cursor:
      Name.append(result[0])  # can also be accessed using result[0]
    cursor.close()
    context = dict(data = Name)
    return render_template("locate.html", **context)

#Search restaurant based on conditions
@app.route('/search', methods=['POST'])
def search():

    pl = request.form['Price_level']
    ct = request.form['Cuisine_Type']
    print pl
    print ct
    cmd = 'SELECT R.Name,R.LongAddress FROM Restaurant R,CuisineType C  WHERE R.Price_level = (:pl1) AND C.Cuisine_Type = (:ct1) AND C.RID = R.RID';
    cursor = g.conn.execute(text(cmd),pl1 = pl,ct1 = ct);
    results = []
    for result in cursor:
        for i in range(len(result)):
            results.append(result[i])  # can also be accessed using result[0]
    cursor.close()
    context = dict(data = results)
    return render_template("search.html", **context)




if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
