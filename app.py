from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flaskext.mysql import MySQL
import mysql.connector
import configparser


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'users'

db = mysql.connector.connect(user='project_user', database='users', password='password123')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods = ["POST","GET"])
def signin():
    if request.method == "POST":
        pass

    

if __name__ == '__main__':
    app.run(debug=True)