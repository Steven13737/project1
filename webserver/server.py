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
import CustomerPageInfo as Cus

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


#define a get result functions
def getresult(cursor):
    results = []
    for result in cursor:
        for i in range(len(result)):
            results.append(result[i])  # can also be accessed using result[0]
    cursor.close()
    #print(results)
    return results


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



@app.route('/logout', methods=['post'])
def logout():
    session.pop('username')
    session['logged_in'] = False
    flash('Logout Success','logout')
    return render_template("index.html")
###########################Log IN #############################################
#Log in Process
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

    print record1

    if record and request.form['attribute'] == 'customer':
        if request.form['attribute'] == 'customer':
            session['logged_in'] = True
            session['username'] = un

            #Search cuisine type
            cui = Cus.GetCuisineType(g,text)

            #Commont Process
            #Get cid
            username = session.get('username')
            CID = Cus.GetCID(g,text,username)
            #print CID
            #Get Restaurant need Commet
            restaurant, crestaurant,crestaurant_time = Cus.GetResuaurant(g,text,CID)
            namedict = Cus.GetDict(crestaurant);
            session['NeedComment'] = namedict;

            #Comine to a list
            cres = []
            j = 0
            for i in range(len(crestaurant_time)):
                cres.append(crestaurant[j] + ","+ str(crestaurant_time[i]))
                j = j+2

            #Vote Process
            VoteRestaurantName,VoteRestaurantName_RID = Cus.VoteRestaurant(g,text,CID)
            votedict = Cus.GetDict(VoteRestaurantName_RID)
            session['NeedVote'] = votedict
            flash('Login scuuess','ok')

            #Get Vote Number:
            Votenum = Cus.Getvotenumber(g,text,CID)
            print Votenum
            votedisplay = Votenum


            #Get History Comment
            commmdisplay = Cus.Gethistorycomment(g,text,CID)

            context2 = dict(cui = cui, restaurants = restaurant, crestaurant = cres, \
                            voterestaurant = VoteRestaurantName,votedisplay = votedisplay,\
                            commmdisplay = commmdisplay )
            return render_template("LogForCustomer.html",**context2)
        else:
            flash('Wrong username or password','no')
            return render_template("index.html")
    if record1:
        if request.form['attribute'] == 'manager':
            session['logged_in'] = True
            session['username'] = un
            cmd_m = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Password = (:pw3) '
            cursor_m = g.conn.execute(text(cmd_m),pw3 = pw)
            r_m = getresult(cursor_m)
            print r_m
            cursor_m.close()
            context_m = dict(data = r_m)
            flash('Login scuuess Manager','okmanager')
            return render_template('LogForManager.html',**context_m)
        else:
            print "abc"
            flash('Wrong username or password','no')
            return render_template("index.html")
    else:
        flash('Wrong username or password','no')
        return render_template("index.html")


########################Sign Up Porcess########################################
#Sign Up
@app.route('/sign')
def sign():
  return render_template("signup.html")

#Sign Up Judgement
@app.route('/signupsuccess', methods=['post'])
def signupsuccess():
    username = request.form['username']
    password = request.form['password']
    name = request.form['name']

    cmd1 = 'SELECT COUNT(*) FROM Customer WHERE Email = (:username1)'
    cursor1 = g.conn.execute(text(cmd1),username1 = username)
    result1 = getresult(cursor1)
    ec = result1[0]
    print ec

    cmd2 = 'SELECT COUNT(*) FROM Manager WHERE Email = (:username1)'
    cursor2 = g.conn.execute(text(cmd2),username1 = username)
    result2 = getresult(cursor2)
    em = result2[0]
    print em

    if not username or not password or not name:
        flash('Email and Password can not be empty','signupfail')
        return render_template('signup.html')
    if request.form['attribute'] == 'customer':

        if ec == 1:
            flash('Email already existed','signupfail')
            return render_template('signup.html')

        cmd_c = 'SELECT max(CID) FROM Customer';
        cursor_c = g.conn.execute(text(cmd_c));
        result_c = []
        for result in cursor_c:
            result_c.append(result[0])
        cursor_c.close()
        cid = int(result_c[0]) + 1
        cmd_c_2 = 'INSERT INTO Customer VALUES (:CID,:Email,:Password,:Name)'

        g.conn.execute(text(cmd_c_2),CID = cid,Email = username, Password = password, Name = name);
        flash('Welcome!','siguupsuccess')
        return render_template("index.html")

    if request.form['attribute'] == 'manager':

        if em == 1:
            flash('Email already existed','signupfail')
            return render_template('signup.html')

        cmd_m = 'SELECT max(MID) FROM Manager';
        cursor_m = g.conn.execute(text(cmd_m));
        result_m = []
        for result in cursor_m:
            result_m.append(result[0])
        cursor_m.close()
        mid = int(result_m[0]) + 1
        cmd_m_2 = 'INSERT INTO Manager VALUES (:MID,:Email,:Password,:Name)'
        g.conn.execute(text(cmd_m_2),MID = mid,Email = username, Password = password, Name = name);
        flash('Welcome!','siguupsuccess')
        return render_template("index.html")



########################Locate and Search for Customers#########################
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
    #cmd = 'SELECT R.Name,R.LongAddress FROM Restaurant R,CuisineType C  WHERE R.Price_level = (:pl1) AND C.Cuisine_Type = (:ct1) AND C.RID = R.RID';
    cmd = 'SELECT R.LongAddress FROM Restaurant R,CuisineType C  WHERE R.Price_level = (:pl1) AND C.Cuisine_Type = (:ct1) AND C.RID = R.RID';
    cursor = g.conn.execute(text(cmd),pl1 = pl,ct1 = ct);
    results = []
    for result in cursor:
        for i in range(len(result)):
            results.append(result[i])  # can also be accessed using result[0]
    cursor.close()
    print(results)
    context = dict(data = results)
    return render_template("search.html", **context)


###############################################################################
#Buy ticket for a restaurants
@app.route('/buy', methods=['POST'])
def buy():
    name2 = request.form['buyname']
    print name2

    #FInd user's cid
    username = session.get('username')
    print username
    cmd = "select CID from Customer where email = (:username)"
    cursor = g.conn.execute(text(cmd),username = username);
    CID = getresult(cursor);
    #print CID


    #Find restaurant's RID
    cmd = "select RID from Restaurant where LongAddress = (:address)"
    cursor = g.conn.execute(text(cmd),address = name2);
    RID = getresult(cursor)
    print RID

    #Get current time
    import time
    date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    print date

    #check if exist
    cmd = "select * from DateConsume where CID =(:CID) and RID = (:RID) and Time_num=(:Date)"
    cursor = g.conn.execute(text(cmd),CID = CID[0], RID = int(RID[0]), Date = date);
    check = getresult(cursor)
    cursor.close()
    if check:
        flash("Please Choose Another Restaurant",'cannotgo')
        #Search cuisine type
        cui = Cus.GetCuisineType(g,text)
        #Commont Process
        #Get cid
        username = session.get('username')
        CID = Cus.GetCID(g,text,username)
        #print CID
        #Get Restaurant need Commet
        restaurant, crestaurant,crestaurant_time = Cus.GetResuaurant(g,text,CID)
        #namedict = Cus.GetDict(crestaurant);
        #session['NeedComment'] = namedict;
        #Comine to a list
        cres = []
        j = 0
        for i in range(len(crestaurant_time)):
            cres.append(crestaurant[j] + ","+ str(crestaurant_time[i]))
            j = j+2

        #Vote Process
        VoteRestaurantName,VoteRestaurantName_RID = Cus.VoteRestaurant(g,text,CID)
        #votedict = Cus.GetDict(VoteRestaurantName_RID)
        #session['NeedVote'] = votedict
        #flash('Login scuuess','ok')

        #Get Vote Number:
        Votenum = Cus.Getvotenumber(g,text,CID)
        #print Votenum
        votedisplay = Votenum


        #Get History Comment
        commmdisplay = Cus.Gethistorycomment(g,text,CID)


        context2 = dict(cui = cui, restaurants = restaurant, crestaurant = cres, \
                        voterestaurant = VoteRestaurantName, votedisplay = votedisplay,\
                        commmdisplay = commmdisplay )
        return render_template("LogForCustomer.html",**context2)


    #Insert new consume record
    cmd = "INSERT INTO DateConsume VALUES (:CID,:RID,:Date)"
    cursor = g.conn.execute(text(cmd),CID = CID[0], RID = int(RID[0]), Date = date);
    flash('Thanks for consume','buysuccess')


    #Add All information in Customer Page#
    #Search cuisine type
    cui = Cus.GetCuisineType(g,text)
    #Commont Process
    #Get cid
    username = session.get('username')
    CID = Cus.GetCID(g,text,username)
    #print CID
    #Get Restaurant need Commet
    restaurant, crestaurant,crestaurant_time = Cus.GetResuaurant(g,text,CID)
    namedict = Cus.GetDict(crestaurant);
    session['NeedComment'] = namedict;
    #Comine to a list
    cres = []
    j = 0
    for i in range(len(crestaurant_time)):
        cres.append(crestaurant[j] + ","+ str(crestaurant_time[i]))
        j = j+2
    #Vote Process
    VoteRestaurantName,VoteRestaurantName_RID = Cus.VoteRestaurant(g,text,CID)
    votedict = Cus.GetDict(VoteRestaurantName_RID)
    session['NeedVote'] = votedict

    #Get Vote Number:
    Votenum = Cus.Getvotenumber(g,text,CID)
    print Votenum
    votedisplay = Votenum

    #Get History Comment
    commmdisplay = Cus.Gethistorycomment(g,text,CID)

    context2 = dict(cui = cui, restaurants = restaurant, crestaurant = cres, \
                    voterestaurant = VoteRestaurantName,votedisplay = votedisplay,\
                    commmdisplay = commmdisplay)


    return render_template("LogForCustomer.html",**context2)


##########################Process Comment#######################################
@app.route('/comment', methods=['POST'])
def comment():
    restaurant = request.form['commentname']
    print restaurant
    comment = request.form['comment']
    print comment

    #Get RID
    name = restaurant.split(",")
    #print name
    restaurants = session.get('NeedComment')
    #print restaurants
    RID = restaurants[name[0]]
    #print RID
    session.pop('NeedComment')

    #Get Date
    date = name[1]
    print date

    #Get cid
    username = session.get('username')
    #print username
    cmd = "select CID from Customer where email = (:username)"
    cursor = g.conn.execute(text(cmd),username = username);
    CID = getresult(cursor);
    print CID

    #Insert Comment
    rate = request.form['rate']
    print rate
    cmd = "INSERT INTO Comment VALUES (:CID, :RID, :date, :rate, :comment)"
    cursor = g.conn.execute(text(cmd), CID = CID[0], RID = int(RID),date = date, rate = float(rate[0]), comment = comment);

    #Add All information in Customer Page#
    #Search cuisine type
    cui = Cus.GetCuisineType(g,text)
    #Commont Process
    #Get cid
    username = session.get('username')
    CID = Cus.GetCID(g,text,username)
    #print CID
    #Get Restaurant need Commet
    restaurant, crestaurant,crestaurant_time = Cus.GetResuaurant(g,text,CID)
    namedict = Cus.GetDict(crestaurant);
    session['NeedComment'] = namedict;
    #Comine to a list
    cres = []
    j = 0
    for i in range(len(crestaurant_time)):
        cres.append(crestaurant[j] + ","+ str(crestaurant_time[i]))
        j = j+2
    #Vote Process
    VoteRestaurantName,VoteRestaurantName_RID = Cus.VoteRestaurant(g,text,CID)
    votedict = Cus.GetDict(VoteRestaurantName_RID)
    session['NeedVote'] = votedict
    flash('Comment Success','CommentSuccess')

    #Get History Comment
    commmdisplay = Cus.Gethistorycomment(g,text,CID)

    #Get Vote Number:
    Votenum = Cus.Getvotenumber(g,text,CID)
    print Votenum
    votedisplay = Votenum

    context2 = dict(cui = cui, restaurants = restaurant, crestaurant = cres, \
                    voterestaurant = VoteRestaurantName,votedisplay = votedisplay,\
                    commmdisplay = commmdisplay )
    return  render_template("LogForCustomer.html",**context2)


@app.route('/vote', methods=['POST'])
def vote():
    restaurant = request.form['votename']
    print restaurant

    #Get RID
    votedict = session.get('NeedVote')
    RID = votedict[restaurant]
    print RID

    #Get cid
    username = session.get('username')
    CID = Cus.GetCID(g,text,username)
    print CID

    #Insert Vote Number
    cmd = "INSERT INTO Vote VALUES (:CID, :RID)"
    cursor = g.conn.execute(text(cmd), CID = CID[0], RID = int(RID));

    #Add All information in Customer Page#
    #Search cuisine type
    cui = Cus.GetCuisineType(g,text)
    #Commont Process
    #Get cid
    username = session.get('username')
    CID = Cus.GetCID(g,text,username)
    #print CID
    #Get Restaurant need Commet
    restaurant, crestaurant,crestaurant_time = Cus.GetResuaurant(g,text,CID)
    namedict = Cus.GetDict(crestaurant);
    session['NeedComment'] = namedict;
    #Comine to a list
    cres = []
    j = 0
    for i in range(len(crestaurant_time)):
        cres.append(crestaurant[j] + ","+ str(crestaurant_time[i]))
        j = j+2
    #Vote Process
    VoteRestaurantName,VoteRestaurantName_RID = Cus.VoteRestaurant(g,text,CID)
    votedict = Cus.GetDict(VoteRestaurantName_RID)
    session['NeedVote'] = votedict

    flash('Vote Success','VoteSuccess')

    #Get Vote Number:
    Votenum = Cus.Getvotenumber(g,text,CID)
    print Votenum
    votedisplay = Votenum


    context2 = dict(cui = cui, restaurants = restaurant, crestaurant = cres, voterestaurant = VoteRestaurantName,votedisplay = votedisplay)
    return  render_template("LogForCustomer.html",**context2)


###############################################################################
############################Manager############################################
@app.route('/add_m', methods=['POST'])
def add_m():
    username = session.get('username')
    n = request.form['Name']
    pl = request.form['Price_Level']
    loca = request.form['Locality']
    lad = request.form['LongAddress']
    lo = float(request.form['Longtitude'])
    la = float(request.form['Latitude'])
    co = request.form['Country']
    c = request.form['City']
    ct = request.form['Cuisine_Type']
    print lo

    cmd8 = 'SELECT COUNT(*) FROM Restaurant WHERE LongAddress = (:lad)'
    cursor8 = g.conn.execute(text(cmd8),lad = lad)
    result8 = getresult(cursor8)
    er = result8[0]

    if er ==1:
        cmd_i = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
        cursor_i = g.conn.execute(text(cmd_i),username = username)
        r_i = getresult(cursor_i)
        print r_i
        cursor_i.close()
        context_i = dict(data = r_i)
        flash('The LongAddress already exists!','Addfail')
        return render_template('LogForManager.html',**context_i)


    cmd = 'INSERT INTO Address VALUES (:loca1, :lad1,:lo1, :la1,:co1,:c1)';
    g.conn.execute(text(cmd),loca1 =loca, lad1 = lad,lo1 = lo, la1 = la, co1 = co, c1 = c);
    cmd2 = 'SELECT max(RID) FROM Restaurant';
    cursor = g.conn.execute(text(cmd2));
    results = []
    for result in cursor:
        results.append(result[0])
    cursor.close()
    rid = int(results[0]) + 1
    print rid
    username = session.get('username')
    cmd3 = 'SELECT MID FROM Manager WHERE Email = (:username)';
    cursor3 = g.conn.execute(text(cmd3),username= username);
    mid = getresult(cursor3)
    cursor3.close()
    print mid
    cmd4 = 'INSERT INTO Restaurant VALUES (:RID,:n1,:pl1,:lad2,:m1)';
    g.conn.execute(text(cmd4),RID = rid, n1 = n, pl1 = pl, lad2 = lad, m1= mid[0]);
    cmd7 = 'SELECT max(ID) FROM CuisineType';
    cursor7 = g.conn.execute(text(cmd7));
    result7 = []
    for result in cursor7:
        result7.append(result[0])
    cursor7.close()
    id = int(result7[0]) + 1
    print id
    cmd6 = 'INSERT INTO CuisineType VALUES(:ID,:RID,:ct)'
    g.conn.execute(text(cmd6),ID = id, RID = rid, ct = ct);
    cmd5 = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
    cursor5 = g.conn.execute(text(cmd5),username = username)
    r5 = getresult(cursor5)
    print r5
    cursor5.close()
    context5 = dict(data = r5)
    flash('Add Restaurant Success','AddSuccess')
    return render_template('LogForManager.html',**context5)

@app.route('/delete_m', methods=['POST'])
def delete_m():
    username = session.get('username')
    n = request.form['Name']
    lad = request.form['LongAddress']
    cmd1 = 'SELECT R.name FROM Restaurant R,Manager M WHERE M.Email = (:username) AND M.MID = R.MID';
    cursor1 = g.conn.execute(text(cmd1),username = username);
    result1 = getresult(cursor1)
    print result1
    cursor1.close()
    count = 0
    for i in range(len(result1)):
        if n == result1[i]:
            count = count + 1
    print count
    if count == 0:
        flash('You do not have this restaurant!')
        cmd4 = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
        cursor4 = g.conn.execute(text(cmd4),username = username)
        r4 = getresult(cursor4)
        print r4
        cursor4.close()
        context4 = dict(data = r4)
        return render_template('LogForManager.html',**context4)
    if count == 1:
        cmd4 = 'SELECT Rid FROM Restaurant WHERE Name = (:name) AND LongAddress = (:lad3)'
        cursor4 = g.conn.execute(text(cmd4),name = n,lad3 = lad)
        result4 = getresult(cursor4)
        cursor4.close()
        rid = result4[0]
        cmd6 = 'DELETE FROM CuisineType WHERE RID = (:RID)'
        g.conn.execute(text(cmd6),RID = rid)
        cmd2 = 'DELETE FROM Restaurant WHERE Name = (:n1) AND LongAddress = (:lad1)'
        g.conn.execute(text(cmd2),n1 = n, lad1 = lad)
        cmd3 = 'DELETE FROM Address WHERE LongAddress = (:lad2)'
        g.conn.execute(text(cmd3),lad2 = lad)
        cmd5 = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
        cursor5 = g.conn.execute(text(cmd5),username = username)
        r5 = getresult(cursor5)
        print r5
        cursor5.close()
        context5 = dict(data = r5)
        flash('Deltet Success','DS')
        return render_template('LogForManager.html',**context5)

@app.route('/update_m', methods=['POST'])
def update_m():
    rid = int(request.form['RID'])
    print rid
    input1 = request.form['input']
    username = session.get('username')
    cmd1 = 'SELECT R.RID FROM Restaurant R,Manager M WHERE M.Email = (:username) AND M.MID = R.MID';
    cursor1 = g.conn.execute(text(cmd1),username = username);
    result1 = getresult(cursor1)
    cursor1.close()
    count = 0
    for i in range(len(result1)):
        if result1[i] == rid:
            count = count + 1
            print count
    if count == 0:
        flash('You do not have this restaurant!')
        cmd4 = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
        cursor4 = g.conn.execute(text(cmd4),username = username)
        r4 = getresult(cursor4)
        print r4
        cursor4.close()
        context4 = dict(data = r4)
        return render_template('LogForManager.html',**context4)
    if count == 1:
        if request.form['attribute'] == 'Name':
            cmd2 = 'UPDATE Restaurant SET Name = (:input1) WHERE RID = (:RID)'
            g.conn.execute(text(cmd2),input1 = input1, RID = rid)
        if request.form['attribute'] == 'Price_Level':

            pl = int(request.form['input'])

            if pl < 1 or pl >4:
                epl = 1
                print epl
                flash('The Price Level is invaild!','Pricefail')
                cmd_i = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
                cursor_i = g.conn.execute(text(cmd_i),username = username)
                r_i = getresult(cursor_i)
                print r_i
                cursor_i.close()
                context_i = dict(data = r_i)
                return render_template('LogForManager.html',**context_i)

            cmd3 = 'UPDATE Restaurant SET Price_Level = (:input1) WHERE RID = (:RID)'
            g.conn.execute(text(cmd3),input1 = input1, RID = rid)
        if request.form['attribute'] == 'Cuisine_Type':
            cmd5 = 'UPDATE CuisineType SET Cuisine_Type = (:input1) WHERE RID = (:RID)'
            g.conn.execute(text(cmd5),input1 = input1, RID = rid)
        cmd4 = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
        cursor4 = g.conn.execute(text(cmd4),username = username)
        r4 = getresult(cursor4)
        print r4
        cursor4.close()
        context4 = dict(data = r4)
        flash('Update Attribute Success','UP')
        return render_template('LogForManager.html',**context4)




@app.route('/update_ad', methods=['POST'])
def update_ad():
    rid = int(request.form['RID'])
    loca = request.form['Locality']
    lad = request.form['LongAddress']
    lo = float(request.form['Longtitude'])
    la = float(request.form['Latitude'])
    co = request.form['Country']
    c = request.form['City']
    username = session.get('username')

    cmd8 = 'SELECT COUNT(*) FROM Address WHERE LongAddress = (:lad)'
    cursor8 = g.conn.execute(text(cmd8),lad = lad)
    result8 = getresult(cursor8)
    er = result8[0]
    print er
    if er == 1:
        flash('The LongAddress already exists!','Addfail')
        cmd_i = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
        cursor_i = g.conn.execute(text(cmd_i),username = username)
        r_i = getresult(cursor_i)
        print r_i
        cursor_i.close()
        context_i = dict(data = r_i)
        return render_template('LogForManager.html',**context_i)

    cmd1 = 'SELECT R.RID FROM Restaurant R,Manager M WHERE M.Email = (:username) AND M.MID = R.MID';
    cursor1 = g.conn.execute(text(cmd1),username = username);
    result1 = getresult(cursor1)
    cursor1.close()
    count = 0
    cmd2 = 'SELECT LongAddress FROM Restaurant WHERE RID = (:rid1)';
    cursor2 = g.conn.execute(text(cmd2),rid1 = rid);
    result2 = getresult(cursor2)
    cursor2.close()
    add = result2[0]
    print add
    for i in range(len(result1)):
        if result1[i] == rid:
            count = count + 1
            print count
    if count == 0:
        flash('You do not have this restaurant!')
        cmd4 = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
        cursor4 = g.conn.execute(text(cmd4),username = username)
        r4 = getresult(cursor4)
        print r4
        cursor4.close()
        context4 = dict(data = r4)
        return render_template('LogForManager.html',**context4)
    if count == 1:
        cmd3 = 'INSERT INTO Address VALUES (:loca1, :lad1,:lo1, :la1,:co1,:c1)';
        g.conn.execute(text(cmd3),loca1 =loca, lad1 = lad,lo1 = lo, la1 = la, co1 = co, c1 = c);
        cmd5 = 'UPDATE Restaurant SET LongAddress = (:lad) WHERE RID = (:RID)'
        g.conn.execute(text(cmd5),lad = lad, RID = rid)
        cmd6 = 'DELETE FROM Address WHERE LongAddress = (:add2)'
        g.conn.execute(text(cmd6),add2 = add)
        cmd4 = 'SELECT R.RID, R.Name, R.Price_Level,R.LongAddress,R.MID FROM Restaurant R, Manager M WHERE R.Mid = M.Mid AND M.Email = (:username)';
        cursor4 = g.conn.execute(text(cmd4),username = username)
        r4 = getresult(cursor4)
        print r4
        cursor4.close()
        context4 = dict(data = r4)
        flash("Update Address Success",'updatead')
        return render_template('LogForManager.html',**context4)
##############################################################################
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
