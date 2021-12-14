import mysql.connector
import pandas as pd
import hashlib

def run_script():
    db = mysql.connector.connect(
        user='project_user2', database='ct_db', password='password123',auth_plugin='mysql_native_password')

    un = pd.read_csv('add_data/usernames.txt')
    pw = pd.read_csv('add_data/passwords.txt')
    fn = pd.read_csv('add_data/fullnames.txt')
    un = un.iloc[0:5000]
    fn = fn.iloc[0:5000]
    uc = 'otlak33'
    fc = 'Aaren'
    pc = 'V76szXAoQ9'
    print(type(un.iloc[0][uc]))
    cur = db.cursor(buffered=True)
    for i in range(un.shape[0]):
        p = hashlib.sha256(str(pw.iloc[i][pc]).encode()).hexdigest()
        cur.execute('insert into solver(full_name,username,password) values(%s,%s,%s)', (fn.iloc[i][fc],un.iloc[i][uc],p))
        db.commit()

if __name__ == '__main__':
    run_script()