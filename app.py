
from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, flash, session,jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
import re

app = Flask(__name__,template_folder="src/views")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
cors = CORS(app, resources={r"/*": {"origins": "*"}})
db = SQLAlchemy(app)


############################################
# 数据库
############################################

# 定义ORM
# User类把我们刚刚创建的几个字段定义为类变量。
# 字段使用db.Column类创建实例，字段的类型作为参数，另外还提供一些其他可选参数
# __repr__方法告诉Python如何打印class对象，方便我们调试使用
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<User %r>' % self.username
        

# 创建表格、插入数据
@app.before_first_request
def create_db():
    db.drop_all()  # 每次运行，先删除再创建
    db.create_all()
    
    admin = User(username='admin', password='root', email='admin@example.com')
    db.session.add(admin)

    guestes = [User(username='guest1', password='guest1', email='guest1@example.com'),
               User(username='guest2', password='guest2', email='guest2@example.com'),
               User(username='guest3', password='guest3', email='guest3@example.com'),
               User(username='guest4', password='guest4', email='guest4@example.com')]
    db.session.add_all(guestes)
    db.session.commit()
    

############################################
# 辅助函数、装饰器
############################################

# 登录检验（用户名、密码验证）
def valid_login(username, password):
    user = User.query.filter(and_(User.username == username, User.password == password)).first()
    if user:
        return True
    else:
        return False

def valid_regist(username, password1, password2, email):
    user = User.query.filter(or_(User.username == username, User.email == email)).first()
    if user:
        return False
    else:
        return True

############################################
# 路由
############################################

# 1.主页
@app.route('/')
# def home():
#     return render_template('Home.vue', username=session.get('username'))

# 2.登录
@app.route('/signin', methods=['GET', 'POST'])
def login():
    response={}
    error = None
    message='测试'
    if request.method == 'POST':
        j_data=request.json
        uname=j_data.get("username")
        p=j_data.get("password")
        if valid_login(uname, p):
            message='登录成功!' 
        else:
            message='用户名或密码错误!'
    response={'msg':message}
    print(response)
    return jsonify(response)

# 3.注册
@app.route('/regist', methods=['GET','POST'])
def regist():
    response={}
    error = None
    if request.method == 'POST':
        j_data=request.json
        uname=j_data.get("username")
        p1=j_data.get("password1")
        p2=j_data.get("password2")
        em=j_data.get("email")
        an=re.search("^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$",em)
        if an == None:
            message='请输入合法的邮箱!'
        elif p1!=p2:
            message='两次输入的密码不一致!'
        elif valid_regist(uname, p1, p2, em):
            user=User(username=uname, password=p1, email=em)
            db.session.add(user)
            db.session.commit()
            message='注册成功!'
        else:
            message='用户名或邮箱重复!'
    response={'msg':message}
    print(response)
    return jsonify(response)




if __name__ == '__main__':
    app.run(debug = True)