from flask import Flask, render_template, url_for, request, redirect, send_from_directory, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flaskext.mysql import MySQL
import mysql.connector
from json import dumps, loads
from types import SimpleNamespace

from werkzeug.utils import send_file
import jwt
from base64 import b64encode
from os import urandom

random_bytes = urandom(64)
key = b64encode(random_bytes).decode('utf-8')


# def encode_token(userid):
#     try:
#         payload = {'sub': userid}
#         return jwt.encode(payload, "\xf9'\xe4p(\xa9\x12\x1a!\x94\x8d\x1c\x99l\xc7\xb7e\xc7c\x86\x02MJ\xa0", algorithm='HS256')
#     except:
#         return Exception


# def decode_token(token):
#     try:
#         payload = jwt.decode(
#             token, "\xf9'\xe4p(\xa9\x12\x1a!\x94\x8d\x1c\x99l\xc7\xb7e\xc7c\x86\x02MJ\xa0")
#         return payload['sub']
#     except jwt.InvalidTokenError:
#         return "Invalid token. Please log in again."


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'project_user'
app.config['MYSQL_PASSWORD'] = 'password123'
app.config['MYSQL_DB'] = 'ct_db'
app.secret_key = key

db = mysql.connector.connect(
    user='project_user', database='ct_db', password='password123')

# USE CASES


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup.html/', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        content = request.get_json()
        cur = db.cursor(buffered=True)
        cur.execute("select username from solver where username = '" +
                    str(content['username']) + "'")
        usernames = cur.fetchall()
        if len(usernames) > 0:
            return jsonify({'valid': 'No'})
        else:
            cur.execute('insert into solver(full_name,username,password) values(%s,%s,%s)',
                        (content['full_name'], content['username'], content['password']))
            db.commit()
            return jsonify({'valid': 'Yes'})

    return render_template('signup.html')


@app.route('/signin.html/', methods=["POST", "GET"])
def signin():
    if request.method == "POST":
        content = request.get_json()
        cur = db.cursor(buffered=True)
        if str(content['selection']) == 'Admin':
            cur.execute("select username from admin where username = '" + str(
                content['username']) + "' and password = '" + str(content['password']) + "'")
            usernames = cur.fetchall()
            if len(usernames) == 0:
                return jsonify({'valid': 'No', 'type': 'Admin'})
            else:
                return jsonify({'valid': 'Yes', 'type': 'Admin'})
        elif str(content['selection']) == 'Solver':
            cur.execute("select user_ID from solver where username = '" + str(
                content['username']) + "' and password = '" + str(content['password']) + "'")
            users = cur.fetchall()
            if len(users) == 0:
                return jsonify({'valid': 'No', 'type': 'Solver'})
            else:
                session['userid']= users[0][0]
                return jsonify({'valid': 'Yes', 'type': 'Solver'})

    return render_template('signin.html')

# DASHBOARDS


@app.route('/dashboard-user.html/')
def dash_user():
    # print('Fit')
    if 'userid' in session:
        return render_template('dashboard-user.html')
    return redirect('/')


@app.route('/dashboard-admin.html/')
def dash_admin():
    return render_template('dashboard-admin.html')

@app.route('/logout/')
def logout():
    session.pop('userid', None)
    return redirect('/')

# IMAGE RENDERING


@app.route('/res/<name>', methods=["GET"])
def fetchImg(name):
    return send_from_directory('Resources', name)


if __name__ == '__main__':
    app.run(debug=True)
