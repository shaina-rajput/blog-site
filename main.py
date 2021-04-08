from flask import Flask, render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
import json
import math
from flask_mail import Mail
pymysql.install_as_MySQLdb()
with open('C:\\Users\\Admin\\Desktop\\first website\\config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key="super-key-secret"
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phoneno = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(12), nullable=True)

class Post(db.Model):
    
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    postedby = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(12), nullable=True)

@app.route('/')
def home():
    posts = Post.query.filter_by().all()
    last=math.ceil(len(posts)/int[0:params['no_of_posts']])
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+int(params['no_of_posts'])]
    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    elif(page==last):
        prev="/?page="+str(page-1)
        next="#"
    else:
        prev="/?page="+str(page-1)
        next="/?page="+str(page+1)
    

    return render_template('index.html', params=params, posts=posts,prev=prev,next=next)

@app.route('/about')
def about():
    return render_template("about.html",params=params)

@app.route('/contact',methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry=Contact(name=name,phoneno=phone, date= datetime.now(),message=message,email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = [params['gmail-user']],
                          body = message + "\n" + phone
                          )
    return render_template("contact.html",params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route('/login', methods=['GET','POST'])
def login():
    if('user' in session and session['user']==params['admin_user']):
        posts=Post.query.all()
        return render_template("adminpanel.html",params=params, posts=posts)
    
    if( request.method=='POST'):
        username=request.form.get('uname')
        userpassword=request.form.get('pass')
        
        if(username == params['admin_user'] and userpassword == params['admin_password']):
            session['user']=username
            posts=Post.query.all()
            return render_template("adminpanel.html",params=params ,posts=posts)
            
    
    return render_template("login.html")

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    if('user' in session and session['user']==params['admin_user']):
        if(request.method=='POST'):
            '''Add entry to the database'''
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            postedby = request.form.get('postedby')
            slug = request.form.get('slug')
            body = request.form.get('body')
            entry=Post(title=title,tagline=tagline,postedby=postedby, date= datetime.now(),body=body,slug=slug)
            db.session.add(entry)
            db.session.commit()
            return redirect('/login')
        return render_template("edit.html")

@app.route('/editpost/<string:sno>', methods=['GET','POST'])
def editpost(sno):
    if('user' in session and session['user']==params['admin_user']):
        if(request.method=='POST'):
            
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            postedby = request.form.get('postedby')
            slug = request.form.get('slug')
            body = request.form.get('body')
            post=Post.query.filter_by(sno=sno).first()
            post.title=title
            post.tagline=tagline
            post.postedby=postedby
            post.body=body
            post.slug=slug
            db.session.commit()
            return redirect('/editpost/'+sno)
        post=Post.query.filter_by(sno=sno).first()
        return render_template("editpost.html",params=params,post=post)

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/login')
       
@app.route('/delete/<string:sno>', methods=['GET','POST'])
def delete(sno):
    if('user' in session and session['user']==params['admin_user']):
        post=Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/login')
       