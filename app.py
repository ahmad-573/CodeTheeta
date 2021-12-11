from os import close
from flask import Flask, render_template, url_for, request, redirect, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from flaskext.mysql import MySQL
import mysql.connector
from json import dumps, loads
from types import SimpleNamespace
import subprocess
from sys import stderr, stdin, stdout
from werkzeug.utils import secure_filename
import os

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
        payload = jwt.decode(token, key, algorithms='HS256')
        return payload['userid'], payload['type_user']
    except jwt.InvalidTokenError:
        return "Invalid"


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'project_user'
app.config['MYSQL_PASSWORD'] = 'password123'
app.config['MYSQL_DB'] = 'ct_db'
app.secret_key = key
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
        cur.execute("select user_ID from solver where username = '" +
                    str(content['username']) + "'")
        users = cur.fetchall()
        if len(users) > 0:
            return jsonify({'valid': 'No'})
        else:
            try:
                cur.execute('insert into solver(full_name,username,password) values(%s,%s,%s)',
                            (content['full_name'], content['username'], content['password']))
                db.commit()
                cur.execute(
                    "select user_ID from solver where username = '" + str(content['username']) + "'")
                users = cur.fetchall()
                return jsonify({'valid': 'Yes', 'token': encode_token(users[0][0], 'Solver')})
            except:
                return jsonify({'valid': 'No'})

    return render_template('signup.html')


@app.route('/signin.html/')
def signin():
    username = request.args.get("username")
    if(username is None):
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


@app.route('/view_problem_user.html/', methods=['GET','POST'])
def view_problem_user():
    token = decode_token(request.args.get("token"))
    if(token == 'Invalid'):
        return redirect('/signin.html')
    p_id = request.args.get("id")
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'file.py'))
        cur = db.cursor(buffered=True)
        # cur.execute(
        # "select problem_id,title,difficulty,statement,test_case1,output1 from problem_set where problem_id = '" + str(p_id) + "'")
        # result1 = cur.fetchall()

        cur.execute(
        "select test_case2,output2 from problem_set where problem_id = '" + str(p_id) + "'")
        result2 = cur.fetchall()
        open('input.txt','w')
        input_file = open('input.txt','a')
        input_string = result2[0][0]
        input_file.write(input_string)
        input_file.close()
        run_file()
        open('correct_output.txt','w')
        cor_output = open('correct_output.txt','a')
        out_string = result2[0][1]
        cor_output.write(out_string)
        cor_output.close()
        

        possible_verdicts = ['Solved','Failed','Compile time error','Runtime error','Time out']
        verdict = possible_verdicts[0]

        return jsonify({'verdict': verdict})

    cur = db.cursor(buffered=True)
    cur.execute(
        "select problem_id,title,difficulty,statement,test_case1,output1 from problem_set where problem_id = '" + str(p_id) + "'")
    result = cur.fetchall()
    cur.execute("select max_score from solved where user_id='" + str(token[0])+"' and problem_id='" + str(p_id) + "'")
    res = cur.fetchall()
    if len(res) == 0:
        score = 0
    else:
        score = res[0][0]
    return render_template('view_problem_user.html', problem=result[0],score=score)

# @app.route('/run_code.html/<int:id>', methods=['GET','POST'])
# def run_code(id):
#     if request.method == 'POST':
#         file = request.files['file']
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'file.py'))
#         cur = db.cursor(buffered=True)
#         cur.execute(
#         "select problem_id,title,difficulty,statement,test_case1,output1 from problem_set where problem_id = '" + str(id) + "'")
#         result1 = cur.fetchall()

#         cur.execute(
#         "select test_case2,output2 from problem_set where problem_id = '" + str(id) + "'")
#         result2 = cur.fetchall()
#         open('input.txt','w')
#         input_file = open('input.txt','a')
#         input_string = result2[0][0]
#         input_file.write(input_string)
#         input_file.close()
#         run_file()

#         return render_template('view_problem_user.html',result=result1)
#     else:  
#         return render_template('run_code.html')

@app.route('/view_problem_admin.html/')
def view_problem_admin():
    token = decode_token(request.args.get("token"))
    if(token == 'Invalid'):
        return redirect('/signin.html')
    p_id = request.args.get("id")
    cur = db.cursor(buffered=True)
    cur.execute(
        "select problem_id,title,difficulty,statement,test_case1,output1 from problem_set where problem_id = '" + str(p_id) + "'")
    result = cur.fetchall()
    return render_template('view_problem_admin.html', result=result)


def update_problem(content):
    cur = db.cursor(buffered=True)
    str2 = content['new']
    str3 = content['id']
    if content['option'] == 'Title':
        str1 = 'title'
    elif content['option'] == 'Statement':
        str1 = 'statement'
    elif content['option'] == 'Test Case 1':
        str1 = 'test_case1'
    elif content['option'] == 'Test Case 2':
        str1 = 'test_case2'
    elif content['option'] == 'Output 1':
        str1 = 'output1'
    elif content['option'] == 'Output 2':
        str1 = 'output2'
    elif content['option'] == 'Difficulty':
        str1 = 'difficulty'
    cur.execute("select * from problem_set where problem_id = "+str(str3))
    if len(cur.fetchall()) == 0:
        success = 'No'
    else:
        try:
            cur.execute("update problem_set set "+str1+" = '" +
                        str(str2) + "' where problem_id = "+str(str3))
            db.commit()
            success = 'Yes'
        except:
            success = "No"
    return {'success': success}


def diff_str_to_int(diff):
    if(diff == 'Easy'):
        return 1
    elif(diff == "Medium"):
        return 2
    elif(diff == "Hard"):
        return 3


@app.route('/delete_problem/')
def delete_problem():
    token = decode_token(request.args.get("token"))
    if(token == 'Invalid'):
        return redirect('/signin.html')
    p_id = request.args.get("id")
    cur = db.cursor(buffered=True)
    cur.execute("delete from problem_set where problem_id = '" +
                str(p_id) + "'")
    db.commit()
    return redirect('/dashboard-admin.html?token='+request.args.get("token"))


# DASHBOARDS
# @app.route('/dashboard-user.html/', methods=['POST', 'GET'], defaults={'res': None})
@app.route('/dashboard-user.html/')
def dash_user():
    # print(request.args.get("token"))
    token = decode_token(request.args.get("token"))
    if(token == 'Invalid'):
        return redirect('/signin.html')
    #    return render_template('signin.html')
    formid = request.args.get('formid')
    if formid is None:
        cur = db.cursor(buffered=True)
        cur.execute(
            "select problem_id, title, difficulty, times_solved, statement from problem_set")
        result = cur.fetchall()

    elif int(formid) == 0:
        cur = db.cursor(buffered=True)
        s1 = 'select problem_id, title, difficulty, times_solved, statement from problem_set where'
        if request.args.get('titlec') != '':
            s1 = s1 + " title like '%" + request.args.get('titlec') + "%'"
        if request.args.get('diff') != '':
            s1 = s1 + ' and difficulty = ' + \
                str(diff_str_to_int(request.args.get('diff')))
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
            s1 = s1 + ' and times_solved' + s2 + request.args.get('value')
        print(s1)
        cur.execute(s1)
        result = cur.fetchall()

    elif int(formid) == 1:
        cur = db.cursor(buffered=True)
        if request.args.get('wrt') == 'Num of time solved':
            str1 = 'times_solved'
        elif request.args.get('wrt') == 'Difficulty Level':
            str1 = 'difficulty'
        if request.args.get('by') == 'Ascending':
            str2 = 'asc'
        elif request.args.get('by') == 'Descending':
            str2 = 'desc'
        cur.execute(
            'select problem_id, title, difficulty, times_solved, statement from problem_set order by '+str1 + ' '+str2)
        result = cur.fetchall()

    return render_template('dashboard-user.html', result=result)


@app.route('/view_ranking_user.html/')
def view_ranking_user():
    token = decode_token(request.args.get("token"))
    if(token == 'Invalid'):
        return redirect('/signin.html')
    cur = db.cursor(buffered=True)
    cur.execute(
        "select username, full_name, points from solver order by points desc")
    result = cur.fetchall()
    return render_template('view_ranking_user.html', result=result)


@app.route('/view_ranking_admin.html/', methods=['POST', 'GET'])
def view_ranking_admin():
    token = decode_token(request.args.get("token"))
    if(token == 'Invalid'):
        return redirect('/signin.html')
    if request.method == 'POST':
        content = request.get_json()
        x = update_points(content)
        return jsonify(x)

    cur = db.cursor(buffered=True)
    cur.execute(
        "select username, full_name, points,user_id from solver order by points desc")
    result = cur.fetchall()
    return render_template('view_ranking_admin.html', result=result)


def update_points(content):
    cur = db.cursor(buffered=True)
    new = content['new']
    id = content['id']
    cur.execute("select * from solver where user_id = "+str(id))
    if len(cur.fetchall()) == 0:
        success = 'No'
    else:
        try:
            cur.execute("update solver set points = '" +
                        str(new) + "' where user_id = "+str(id))
            db.commit()
            success = 'Yes'
        except:
            success = 'No'
    return {'success':success}
    


@app.route('/dashboard-admin.html/', methods=["GET", "POST"])
def dash_admin():
    token = decode_token(request.args.get("token"))
    if(token == 'Invalid'):
        return redirect('/signin.html')

    if request.method == 'POST':
        content = request.get_json()
        formid = content['formid']

        if formid == 0:
            cur = db.cursor(buffered=True)
            try:
                cur.execute('insert into problem_set(title,difficulty, statement, test_case1, test_case2, output1, output2) values(%s,%s,%s,%s, %s,%s,%s)',
                            (content['title'], content['difficulty'], content['statement'], content['tc1'], content['tc2'], content['o1'], content['o2']))
                db.commit()
                cur.execute('select max(problem_id) from problem_set')
                id = cur.fetchall()[0][0]
                cur.execute('insert into created values(%s,%s)',(id,token[0]))
                db.commit()
                success = 'Yes'
            except:
                success = 'No'
            return jsonify({'success': success})

        elif formid == 1:
            return jsonify(update_problem(content))

        elif formid == 2:
            cur = db.cursor(buffered=True)
            try:
                cur.execute('insert into admin(referral_id,full_name,username,password) values(%s,%s,%s,%s)',
                            (token[0], content['fullname'], content['username'], content['password']))
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


def run_file():
    inp = open('input.txt','r')
    open('output.txt','w')

    input_str = ''
    for line in inp:
        input_str = input_str + ' ' + line

    with open('output.txt','a') as f:
        p = subprocess.Popen('python uploads/file.py', shell=True, stdout=f, stdin=subprocess.PIPE ,text=True)
        p.communicate(input_str)

# # IMAGE RENDERING


@app.route('/res/<name>', methods=["GET"])
def fetchImg(name):
    return send_from_directory('Resources', name)


if __name__ == '__main__':
    app.run(debug=True)
