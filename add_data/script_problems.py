import mysql.connector
import pandas as pd
import hashlib
from random import randint
import random

def get_shuffled_substr(s):
    n = len(s)
    start = randint(0,n-1)
    end = randint(start+1,n)
    l = list(s[start:end])
    random.shuffle(l)
    return ''.join(l)

    


def run_script():
    db = mysql.connector.connect(
        user='project_user2', database='ct_db', password='password123',auth_plugin='mysql_native_password')
    og_title = 'Thisisarandomtitlegenerator'
    lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mauris non imperdiet sem, ac malesuada mi. Mauris sed nunc nisi. Duis vitae semper purus. Aliquam dolor enim, aliquam id urna sed, dignissim tincidunt ipsum. Proin fringilla mauris bibendum augue venenatis laoreet sit amet id nisl. Mauris feugiat nisi tristique ante facilisis, sed auctor nisi pulvinar. Nam in velit porttitor, accumsan felis ut, imperdiet neque. Praesent ac fringilla ex. Fusce volutpat tellus vitae tellus scelerisque faucibus. Vivamus commodo molestie nisl non facilisis. Donec sollicitudin velit felis, non malesuada ligula vestibulum eu.'
    cur = db.cursor(buffered=True)
    for i in range(5000):
        title = get_shuffled_substr(og_title)
        difficulty = randint(1,3)
        cur.execute("insert into problem_set(title,difficulty,statement,test_case1,test_case2,output1,output2) values(%s,%s,%s,%s,%s,%s,%s)",(title,difficulty,lorem,lorem,lorem,lorem,lorem))
        db.commit()
        cur.execute("select max(problem_id) from problem_set")
        r = cur.fetchall()[0][0]
        r = int(r)
        cur.execute("insert into created values(%s,%s)",(r,7))
        db.commit()


    

if __name__ == '__main__':
    run_script()