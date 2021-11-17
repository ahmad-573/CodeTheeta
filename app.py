from flask import Flask, render_template, url_for, request, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flaskext.mysql import MySQL
import mysql.connector

from werkzeug.utils import send_file


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'project_user'
app.config['MYSQL_PASSWORD'] = 'password123'
app.config['MYSQL_DB'] = 'ct_db'

db = mysql.connector.connect(user='project_user', database='ct_db', password = 'password123')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup.html/', methods = ["POST","GET"])
def signup():
    error = None
    if request.method == "POST":
        name = request.form['name']
        username = request.form['username']
        passwd = request.form['password']
        cur = db.cursor(buffered=True)
        cur.execute("select username from solver where username = '" + str(username) + "'")
        usernames = cur.fetchall()
        if len(usernames) > 0:
            error = "Bhaiiii ye username pehle se hai kuch aur rakho"
            #return redirect('/signup.html')
        else:
            cur.execute('insert into solver(full_name,username,password) values(%s,%s,%s)',(name,username,passwd))
            db.commit()
            return redirect('/')

   
    return render_template('signup.html',error = error)


@app.route('/signin.html/', methods = ["POST","GET"])
def signin():
    error = None
    if request.method == "POST":
        username = request.form['username']
        passwd = request.form['password']
        cur = db.cursor(buffered=True)
        cur.execute("select username from solver where username = '" + str(username) + "' and password = '" + str(passwd) + "'")
        usernames = cur.fetchall()
        if len(usernames) == 0:
            error = "Bhaiii aap pehle account to bana lo ya details theek krlo"
        else:
            return redirect('/')
        
    
    
    return render_template('signin.html', error = error)

@app.route('/res/<name>', methods = ["GET"])
def fetchImg(name):
    print('here')
    return send_from_directory('Resources', name)
if __name__ == '__main__':
    app.run(debug=True)