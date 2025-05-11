import flask
import mysql.connector
import hashlib
from flask import request, jsonify, render_template,Flask,session

app = Flask(__name__)

c = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Q1w2e3r4t5y6u7i8o9p0',
    'database': 'test',
    'port': 3306
}

session=flask.session
app.secret_key='secret'

def connect(c):
    
    with mysql.connector.connect(**c) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT number,title from todo')
        data = cursor.fetchall()
    return data

@app.route('/')
def index():
    if session:
        print(session)
        with mysql.connector.connect(**c) as conn:
            cursor = conn.cursor()
            username=session['username']
            cursor.execute("Select userid from todousers where username=(%s)",(username,))
            id=cursor.fetchall()[0][0]
            cursor.execute('SELECT id,number,title from todo where userid=(%s)',(id,))
            data = cursor.fetchall()
            print(data)
        return render_template('tasks.html', data=data)
    return render_template('login.html')
    
@app.route('/register',methods=['POST','GET'])
def register():
    if request.method=='GET':
        return render_template('regster.html')
    if request.method=='Post':
        username=request.get_json()['username']
        password=request.get_json()['password']
        password=hashlib.md5(str(password).encode('utf-16')).hexdigest()

        with mysql.connector.connect(**c) as conn:
            cursor = conn.cursor()
            cursor.execute("Select * from todousers")
            todo=cursor.fetchall()
            cursor.execute("INSERT INTO todousers (username,password,userid) VALUES (%s,%s,%s)",(username,password,len(todo)+1))
            conn.commit()
            session['username']=username
            print(5)
        return jsonify({"status":200,"text":"OK"})
    
        
    


@app.route("/add", methods=["POST"])
def add():
    username=session['username']
    TaskName=request.get_json()["task"]
    TaskName=str(TaskName).strip()
    with mysql.connector.connect(**c) as conn:
        cursor = conn.cursor()
        cursor.execute("select userid from todousers where username=(%s)",(username,))
        id=cursor.fetchall()[0][0]
        cursor.execute('INSERT INTO todo (number,title,userid) VALUES (%s,%s,%s)', (len(connect(c))+1,TaskName,id))
        conn.commit()

    return (jsonify({"status":201,"text":"OK"}))

@app.route("/delete", methods=["POST"])
def delete():
    try:
        Task=request.get_json()["task"]
        with mysql.connector.connect(**c) as conn:
            cursor = conn.cursor()
            cursor.execute("delete from todo where title=(%s)",(Task,))
            conn.commit()
        return jsonify({"status":200,"text":"OK"})
    except Exception as e:
        return jsonify({"status":400,"text":str(e)})



@app.route('/login',methods=['POST'])
def login():
    print(session)
    username=request.get_json()['username']
    password=request.get_json()['password']
    password=hashlib.md5(str(password).encode('utf-16')).hexdigest()

    with mysql.connector.connect(**c) as conn:
        cursor = conn.cursor()

        cursor.execute("Select * from todousers where username=(%s) ",(username,))
        if cursor.fetchall():
            print(1)
            cursor.fetchall()
            cursor.execute("Select * from todousers where password=(%s) ",(password,))

            if not cursor.fetchall(): 
                print(2)
                return jsonify({"status":409,'text':"Username already exists please specify another"})
        cursor.execute("Select * from todousers where username=(%s) and password=(%s)",(username,password))
    
        if cursor.fetchall():
            print(3)
            session['username']=username
            return jsonify({"status":200,'text':"user already exist"})
    return jsonify({"status":204,'text':"User does not exist please register first"})



app.run(debug=True,host='0.0.0.0',port=5001)