from flask import Flask, request, render_template, redirect, flash, session
import md5

app = Flask(__name__)
app.secret_key = 'myothersecretkey'

from mysqlconnection import MySQLConnector
mysql = MySQLConnector(app, 'login_and_registration_db')

import re
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")

#first checks to see if session id is recognizable. If yes (not equal to None), then directs first to the success page. 
@app.route('/')
def index():
    if session.get('id') != None:
        return redirect('/success')
    return render_template('index.html')

@app.route('/success')
def member():
    if session.get('id') == None:
        return redirect('/')
    return render_template('success.html')

@app.route('/register', methods=['POST'])
def register():
    session['fname'] = request.form['fname'] #session['fname'] is the value from the fields in index.html, request.form['fname'] tells us where in the form to pull that info from
    session['lname'] = request.form['lname']
    session['email'] = request.form['email']
    session['password'] = request.form['password']
    session['password_confirm'] = request.form['password_confirm']
    print session['fname']
    
    fname_valid = False
    lname_valid = False
    email_valid = False
    password_valid = False
    confirm_password_valid = False

    query = "SELECT * FROM users WHERE email = :email"
    data = {
        'email': session['email']
    }
    user_info = mysql.query_db(query, data)

    if len(user_info) != 0:
        flash('email is taken')
        return redirect('/')


    if session['fname'].isalpha() and len(session['fname']) > 1:
        fname_valid = True
    else:
        if not session['fname'].isalpha():
            flash('first name must contain only letters')
        if len(session['fname']) < 2:
            flash('first name must contain at least 2 letters') 


    if session['lname'].isalpha() and len(session['lname']) > 1:
        lname_valid = True
    else:
        if not session['lname'].isalpha():
            flash('last name must contain only letters')
        if len(session['lname']) < 2:
            flash('last name must contain at least 2 letters')
        

    if EMAIL_REGEX.match(session['email']):
        email_valid = True
    else:
        flash('email entered must be valid email address')


    if len(session['password']) > 8:
        password_valid = True
    else:
        flash('password must contain at least 8 characters')


    if session['password'] == session['password_confirm']:
        confirm_password_valid = True
    else:
        flash('passwords do not match')


    if fname_valid and lname_valid and email_valid and password_valid and confirm_password_valid:
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:fname, :lname, :email, :password, NOW(), NOW())"

        #below data should define where the VALUES come from in the above query. So we use the key from index.html in Values and below rather than the column name in DB (column names are indicated in query after table "users" is named..)
        data = {
            'fname': session['fname'],
            'lname': session['lname'],
            'email': session['email'],
            'password': md5.new(request.form['password']).hexdigest()
        }

        mysql.query_db(query, data) #sends above query to db so users are actually inserted into db 
        
        query = "SELECT * FROM users WHERE fname =:fname, lname=:lname, email = :email"
        data = {
            'fname': session['fname'],
            'lname': session['lname'],
            'email': session['email']
        }
        verified_user = mysql.query_db(query, data)
        session.clear()
        session['id'] = verified_user[0]['id']
        session['fname'] = verified_user[0]['fname']
        return redirect('/')
        #return redirect('/success')
        #return render_template('success.html') #info is sent to db and success.html is displayed.
    else:
        return redirect('/')


@app.route('/login', methods=['POST'])
def login(): 
    session['email'] = request.form['email']
    session['password'] = request.form['password']

    #selects all data from db row where email entered in form matches email in db AND password in form match password stored in db FOR THAT EMAIL address
    query = "SELECT * FROM users WHERE email=:email AND password=:password"
    data = {
        'email': email,
        'password': md5.new(password).hexdigest()
    }
    verified_user = mysql.query_db(query, data)

    if len(verified_user) != 0:
        session['id'] = verified_user[0]['id']
        session['fname'] = verified_user[0]['first_name']
        return render_template('success.html')
    else:
        flash('username and password do not match')
        return redirect('/')

app.run(debug=True)