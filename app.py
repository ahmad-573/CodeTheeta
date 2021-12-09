from flask import Flask, render_template, url_for, request, redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flaskext.mysql import MySQL
import mysql.connector
from json import dumps, loads
from types import SimpleNamespace
import jwt
from base64 import b64encode
from os import urandom
from werkzeug.utils import send_file

random_bytes = urandom(64)
key = b64encode(random_bytes).decode('utf-8')

def encode_token(userid, type_user):
    try:
        payload = {'userid': userid, 'type_user': type_user}
        return jwt.encode(payload, key, algorithm='HS256')
    except:
        return Exception


def decode_token(token):
    try:
        payload = jwt.decode(token, key, algorithms = 'HS256')
        return payload['userid'], payload['type_user']
    except jwt.InvalidTokenError:
        return "Invalid"



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


@app.route('/signin.html/', methods=["GET"])
def signin():
    username = request.args.get("username")
    if(username is None):
        # print('yooooo')
        return render_template('signin.html')
    else:   
        password = request.args.get("password")
        selection = request.args.get("selection")
        cur = db.cursor(buffered=True)
        if str(selection) == 'Admin':
            cur.execute("select admin_id from admin where username = '" + str(
                username) + "' and password = '" + str(password) + "'")
            users = cur.fetchall()
            if len(users) == 0:
                return jsonify({'valid': 'No', 'type': 'Admin'})
            else:
                return jsonify({'valid': 'Yes', 'type': 'Admin', 'token': encode_token(users[0][0], 'Admin')})
        elif str(selection) == 'Solver':
            cur.execute("select user_ID from solver where username = '" + str(
                username) + "' and password = '" + str(password) + "'")
            users = cur.fetchall()
            if len(users) == 0:
                return jsonify({'valid': 'No', 'type': 'Solver'})
            else:
                # print(encode_token(users[0][0], 'Solver'))
                return jsonify({'valid': 'Yes', 'type': 'Solver', 'token': encode_token(users[0][0], 'Solver')})


@app.route('/view_problem_user/<int:id>')
def view_problem_user(id):
    cur = db.cursor(buffered=True)
    cur.execute(
        "select problem_id,title,difficulty,statement,test_case1,output1 from problem_set where problem_id = '" + str(id) + "'")
    result = cur.fetchall()
    return render_template('view_problem_user.html', result=result)

@app.route('/view_problem_admin/<int:id>')
def view_problem_admin(id):
    cur = db.cursor(buffered=True)
    cur.execute(
        "select problem_id,title,difficulty,statement,test_case1,output1 from problem_set where problem_id = '" + str(id) + "'")
    result = cur.fetchall()
    return render_template('view_problem_admin.html', result=result)



def update_problem(content):
    cur = db.cursor(buffered=True)
    str2 = content['new']
    str3 = content['id']
    if content['option']=='Title':
        str1 = 'title'
    elif content['option']=='Statement':
        str1 = 'statement'
    elif content['option']=='Test Case 1':
        str1 = 'test_case1'
    elif content['option']=='Test Case 2':
        str1 = 'test_case2'
    elif content['option']=='Output 1':
        str1 = 'output1'
    elif content['option']=='Output 2':
        str1 = 'output2'
    elif content['option']=='Difficulty':
        str1 = 'difficulty'
    cur.execute("select * from problem_set where problem_id = "+str(str3))
    if len(cur.fetchall())== 0:
        success = 'No'
    else:
        try:
            
            cur.execute("update problem_set set "+str1+" = '"+ str(str2) +"' where problem_id = "+str(str3))
            db.commit()
            success = 'Yes'
        except:
            success = 'No'
            # print("Yooo")
    return {'success': success}
    

@app.route('/delete_problem/<int:id>')
def delete_problem(id):
    cur = db.cursor(buffered=True)
    cur.execute("delete from problem_set where problem_id = '" + str(id) + "'")
    db.commit()
    return redirect('/dashboard-admin.html')


# DASHBOARDS
# @app.route('/dashboard-user.html/', methods=['POST', 'GET'], defaults={'res': None})
@app.route('/dashboard-user.html/', methods=['POST', 'GET'])
def dash_user():
    # print(request.args.get("token"))
    token = decode_token(request.args.get("token"))
    if(token == 'Invalid'):
        return redirect('/signin.html')
    formid = request.args.get('formid')
    if formid is None:
        cur = db.cursor(buffered=True)
        cur.execute("select problem_id, title, difficulty, times_solved, statement from problem_set")
        result = cur.fetchall()

    elif formid == 0:
        cur = db.cursor(buffered=True)
        s1 = 'select problem_id, title, difficulty, times_solved, statement from problem_set where'
        if request.args.get('titlec') != '':
            s1 = s1 + ' title = ' + request.args.get('titlec')
        if request.args.get('diff') != '':
            s1 = s1 + ' difficulty = ' + request.args.get('diff')
        if request.args.get('value') != '':
            if request.args.get('nots') == 'equals':
                s2 = ' = '
            elif request.args.get('nots') == 'less than':
                s2 = ' < '
            elif request.args.get('nots') == 'greater than':
                s2 = ' > '
            elif request.args.get('nots') == 'less than equal to':
                s2 = ' <= '
            elif request.args.get('nots') == 'greater than equal to':
                s2 = ' >= '
            s1 = s1 + ' times_solved' + s2 + request.args.get('value')
        cur.execute(s1)
        result = cur.fetchall()   

    elif formid == 1:
        cur = db.cursor(buffered=True)
        if request.args.get('wrt')=='Num of time solved':
            str1 = 'times_solved'
        elif request.args.get('wrt')=='Difficulty Level':
            str1 = 'difficulty'
        if request.args.get('by')=='Ascending':
            str2 = 'asc'
        elif request.args.get('by')=='Descending':
            str2 = 'desc'
        cur.execute('select problem_id, title, difficulty, times_solved, statement from problem_set order by '+str1 +' '+str2)
        result = cur.fetchall()

    return render_template('dashboard-user.html', result=result)


@app.route('/view_ranking_user.html/')
def view_ranking_user():
    cur = db.cursor(buffered=True)
    cur.execute("select username, full_name, points from solver order by points desc")
    result = cur.fetchall()
    return render_template('view_ranking_user.html',result=result)

@app.route('/view_ranking_admin.html/', methods=['POST','GET'])
def view_ranking_admin():
    if request.method == 'POST':
        content = request.get_json()
        if content['formid'] == 0:
            pass
        elif content['formid'] == 1:
            x = update_points(content)
            return jsonify(x)
        

    cur = db.cursor(buffered=True)
    cur.execute("select username, full_name, points,user_id from solver order by points desc")
    result = cur.fetchall()
    return render_template('view_ranking_admin.html',result=result)

def update_points(content):
    cur = db.cursor(buffered=True)
    new = content['new']
    id = content['id']
    cur.execute("select * from solver where user_id = "+str(id))
    if len(cur.fetchall())== 0:
        success = 'No'
    else:
        try:
            cur.execute("update solver set points = '"+ str(new) +"' where user_id = "+str(id))
            db.commit()
            success = 'Yes'
        except:
            success = 'No'
    return {'success':success}
        

@app.route('/dashboard-admin.html/',  methods=['POST', 'GET'])
def dash_admin():
    
    if request.method == "POST":
        content = request.get_json()
        # print(content['title'])
        # print("hello")
        if content['formid'] == 0:
            cur = db.cursor(buffered=True)
            try:
                cur.execute('insert into problem_set(title,difficulty, statement, test_case1, test_case2, output1, output2) values(%s,%s,%s,%s, %s,%s,%s)',
                            (content['title'],content['difficulty'], content['statement'], content['tc1'], content['tc2'], content['o1'], content['o2']))

                db.commit()
                success = 'Yes'
            except:
                success = 'No'
            return jsonify({'success': success})
        elif content['formid'] == 1:
            x = update_problem(content)
            return jsonify(x)
        elif content['formid'] == 2:
            cur = db.cursor(buffered=True)
            try:
                cur.execute('insert into admin(referral_id,full_name,username,password) values(%s,%s,%s,%s)', ('1',content['fullname'],content['username'],content['password']))
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
