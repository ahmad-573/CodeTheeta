from flask import Flask, render_template, url_for, request, redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flaskext.mysql import MySQL
import mysql.connector
from json import dumps, loads
from types import SimpleNamespace

from werkzeug.utils import send_file


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'project_user'
app.config['MYSQL_PASSWORD'] = 'password123'
app.config['MYSQL_DB'] = 'ct_db'

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
            cur.execute("select username from solver where username = '" + str(
                content['username']) + "' and password = '" + str(content['password']) + "'")
            usernames = cur.fetchall()
            if len(usernames) == 0:
                return jsonify({'valid': 'No', 'type': 'Solver'})
            else:
                return jsonify({'valid': 'Yes', 'type': 'Solver'})

    return render_template('signin.html')


@app.route('/view_problem/<int:id>')
def view_problem(id):
    cur = db.cursor(buffered=True)
    cur.execute(
        "select problem_id,difficulty,statement from problem_set where problem_id = '" + str(id) + "'")
    result = cur.fetchall()
    return render_template('view_problem.html', result=result)

@app.route('/update_problem.html/', methods=['POST', 'GET'])
def update_problem():
    result = None
    if request.method == "POST":
        cur = db.cursor(buffered=True)
        str2 = request.form['new']
        str3 = request.form['id']
        if request.form['options']=='Title':
            str1 = 'title'
        elif request.form['options']=='Statement':
            str1 = 'statement'
        elif request.form['options']=='Test Case 1':
            str1 = 'test_case1'
        elif request.form['options']=='Test Case 2':
            str1 = 'test_case2'
        elif request.form['options']=='Output 1':
            str1 = 'output1'
        elif request.form['options']=='Output 2':
            str1 = 'output2'
        elif request.form['options']=='Difficulty':
            str1 = 'difficulty'
        # print(str1,str2,str3)
        # print(type(str1),type(str2), type(str3))
        cur.execute("update problem_set set "+str1+" = '"+ str(str2) +"' where problem_id = "+str(str3))
    elif request.method == 'GET':
        cur = db.cursor(buffered=True)
        cur.execute(
            "select problem_id, title, difficulty, times_solved, statement from problem_set")
        result = cur.fetchall()
    return render_template('update_problem.html', result=result)

@app.route('/delete_problem/<int:id>')
def delete_problem(id):
    cur = db.cursor(buffered=True)
    cur.execute("delete from problem_set where problem_id = '" + str(id) + "'")
    db.commit()
    return redirect('/dashboard-admin.html')


# DASHBOARDS
@app.route('/dashboard-user.html/', methods=['POST', 'GET'])
def dash_user():
    if request.method == "POST":
        cur = db.cursor(buffered=True)
        if request.form['wrt']=='Num of time solved':
            str1 = 'times_solved'
        elif request.form['wrt']=='Difficulty Level':
            # print("yo")
            str1 = 'difficulty'
        if request.form['by']=='Ascending':
            str2 = 'asc'
        elif request.form['by']=='Descending':
            # print('yo2')
            str2 = 'desc'
        cur.execute('select problem_id, title, difficulty, times_solved, statement from problem_set order by '+str1 +' '+str2)
        result = cur.fetchall()
    elif request.method == 'GET':
        cur = db.cursor(buffered=True)
        cur.execute(
            "select problem_id, title, difficulty, times_solved, statement from problem_set")
        result = cur.fetchall()
    # print('hello')    
    return render_template('dashboard-user.html', result=result)


@app.route('/dashboard-admin.html/',  methods=['POST', 'GET'])
def dash_admin():
    if request.method == "POST":
        content = request.get_json()
        # print(type(content['difficulty']), content['difficulty'])
        cur = db.cursor(buffered=True)
        try:
            cur.execute('insert into problem_set(title,difficulty, statement, test_case1, test_case2, output1, output2) values(%s,%s,%s,%s, %s,%s,%s)',
                        (content['title'],content['difficulty'], content['statement'], content['tc1'], content['tc2'], content['o1'], content['o2']))

            db.commit()
            success = 'Yes'
        except:
            success = 'No'
        return jsonify({'success': success})

    cur = db.cursor(buffered=True)
    cur.execute(
        "select problem_id, title, difficulty, times_solved, statement from problem_set")
    result = cur.fetchall()
    return render_template('dashboard-admin.html', result=result)

# IMAGE RENDERING


@app.route('/res/<name>', methods=["GET"])
def fetchImg(name):
    return send_from_directory('Resources', name)


if __name__ == '__main__':
    app.run(debug=True)
