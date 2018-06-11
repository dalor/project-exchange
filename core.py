from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
from werkzeug import generate_password_hash, check_password_hash
import sqlite3
import os
import smtplib
import string
import re
from validate_email import validate_email #pip install validate_email #pip install pyDNS
from random import choice
import time

app = Flask(__name__)
#app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db.db'),
    URL='https://project-exchange.herokuapp.com/',
    DEBUG=True,
    MIN_LOGIN=6,
    MAX_LOGIN=64,
    MIN_PASSWORD=6,
    MAX_PASSWORD=64,
    PROJECTS_PER_PAGE=8,
    SECRET_KEY='key',
    USERNAME='admin',
    PASSWORD='admin',
    MAIL='service.register.project@gmail.com',
    MAIL_PASSWORD='register228',
    SMTP_SERVER='smtp.gmail.com:587'
))
#app.config.from_envvar('PROPERTIES', silent=True)
def send_mail(to_addr, subject, body_text):
    BODY = "\r\n".join((
        "From: %s" % app.config['MAIL'],
        "To: %s" % to_addr,
        "Subject: %s" % subject ,
        "",
        body_text
    ))
    mmail = smtplib.SMTP(app.config['SMTP_SERVER'])
    mmail.starttls()
    mmail.ehlo()
    mmail.login(app.config['MAIL'],app.config['MAIL_PASSWORD'])
    mmail.sendmail(app.config['MAIL'], [to_addr], BODY)
    mmail.quit()
    
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def index():
    return pages(1)

@app.route('/reg', methods=['POST'])
def registr():
    if session.get('logged_in'):
        return jsonify({'ok': False, 'errors':['You are already logged']})
    errors = []
    if len(request.form['username']) < app.config['MIN_LOGIN'] or len(request.form['username']) > app.config['MAX_LOGIN']:
        errors.append("Choose other login lenth  <br>") #LOGIN ERROR
    if len(request.form['password']) < app.config['MIN_PASSWORD'] or len(request.form['password']) > app.config['MAX_PASSWORD']:
        errors.append("Choose other password lenth  <br>") #PASSWORD ERROR
    db = get_db()
    if not bool(re.match('^[A-Za-z0-9]*$', request.form['username'])):
        errors.append("Create new login  <br>")
    elif db.execute('select * from users where login = ?',  [request.form['username']]).fetchone():
        errors.append("We have such login  <br>")     #LOGIN WE HAVE ERROR
    if not validate_email(request.form['email']):
        errors.append("E-mail is not valid  <br>")
    elif db.execute('select * from users where email = ?',  [request.form['email']]).fetchone():
        errors.append("We have such e-mail  <br>")    #MAIL WE HAVE ERROR
    if len(errors) > 0:
        return jsonify({'ok': False, 'errors':errors})
    db.execute('insert into users (login, password, email, name, status) values (?, ?, ?, ?, ?)',
    [request.form['username'], generate_password_hash(request.form['password']), request.form['email'], request.form['name'], "unchecked"])
    hash_ = "".join(choice(string.ascii_letters + string.digits) for x in range(64))
    print(request.form)
    db.execute('insert into check_users (login, check_hash, type, status) values (?, ?, ?, ?)', [request.form['username'], request.form['username']+"-"+hash_ , "email", request.form['type']])
    mess_text = render_template("mess.html",url=app.config['URL']+"check?hash="+request.form['username']+"-"+hash_)
    send_mail(request.form['email'], 'Accept registration', mess_text)
    db.commit()
    return jsonify({'ok': True})
    
@app.route('/check', methods=['GET'])
def check():
    if session.get('logged_in'):
        return redirect(url_for('index'))
    db = get_db()
    cch = db.execute('select login, status from check_users where check_hash = ?',  [request.args.get('hash')]).fetchone()
    if cch:
        clogin = cch[0]
        db.execute("update users set status = ? where login = ?",  [cch[1], clogin])
        db.execute('delete from check_users where check_hash = ?',  [request.args.get('hash')])
        db.commit()
    return redirect(url_for('index'))
        
@app.route('/write')
def write():
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    return render_template('write.html', title="Add project")
    
@app.route('/write_s', methods=['POST'])
def write_s():
    if not session.get('logged_in'):
        return jsonify({'ok': False, 'errors':['You are not logged']})
    db = get_db()
    db.execute('insert into tasks (login, title, description, content, date, deadline, max_people, now_people, subject) values (?, ?, ?, ?, ?, ?, ?, 0, ?)',
    [session['login'], request.form['title'],request.form['description'],request.form['content'],time.strftime("%Y-%m-%d"),request.form['deadline'],request.form['max_people'], request.form['subject']])
    db.commit()
    return jsonify({'ok': True})
    
@app.route('/work_s', methods=['POST'])
def work_s():
    if not session.get('logged_in'):
        return jsonify({'ok': False, 'errors':['You are not logged']})
    db = get_db()
    print(request.form)
    db.execute('update works set content = ? where task = ? and login = ?',
    [request.form['content'], request.form['id'], session['login']])
    db.commit()
    return jsonify({'ok': True})

@app.route('/log', methods=['POST'])
def login():
    if session.get('logged_in'):
        return jsonify({'ok': False, 'errors':['You are already logged']})
    db = get_db()
    reqq = db.execute('select password, status, name from users where login = ?',  [request.form['username']]).fetchone()
    if reqq and check_password_hash(reqq[0], request.form['password']):
        if reqq[1] == "unchecked":
            jsonify({'ok': False, 'errors':['Check your e-mail']})
        if reqq[1] == "employer":
             session['employer'] = True
        if reqq[1] == "employee":
             session['employee'] = True
        elif reqq[1] == "admin":
            session['admin'] = True
        session['logged_in'] = True
        session['login'] = request.form['username']
        session['name'] = reqq[2]
        return jsonify({'ok': True})
    else:
        return jsonify({'ok': False, 'errors':['Login or password is not valid']})

@app.route('/logout')
def log_out_to():
    session.clear()
    return redirect(url_for('index'))
    
@app.route('/task/<int:id>')
def project(id):
    db = get_db()
    proj = db.execute('select * from tasks where id = ?',  [int(id)]).fetchone()
    wo = None
    re = None
    if session.get('employee') and proj:
        work = db.execute('select content from works where task = ? and login = ?',  [proj[0], session['login']]).fetchone()
        if work:
            wo = work[0]
    elif session.get('employer') and proj:
        re = db.execute('select content, login from works where task = ?',  [proj[0]])
    if proj:
        return render_template('project.html', p=proj, w = wo, r = re, title="Project: " + proj[2])
    else:
        return redirect(url_for('index'))
        
#@app.route('/project_un/<int:id>')
#def project_un(id):
#    db = get_db()
#    proj = db.execute('select * from unpublished_projects where id = ?',  [int(id)]).fetchone()
#    if proj:
#        return render_template('project.html', p=proj, title="Project: " + proj[2])
#    else:
#        return redirect(url_for('index'))
        
@app.route('/edit/<int:id>')
def edit_p(id):
    if not session.get('employer'):
        return redirect(url_for('index'))
    db = get_db()
    proj = db.execute('select * from tasks where id = ? and login = ?',  [int(id), session['login']]).fetchone()
    if proj:
        return render_template('edit.html', p=proj, title="Edit: " + proj[2])
    else:
        return redirect(url_for('index'))

#@app.route('/edit_un/<int:id>')
#def edit_un(id):
#    if not session.get('editor'):
#        return redirect(url_for('index'))
#    db = get_db()
#    proj = db.execute('select * from unpublished_projects where id = ?',  [int(id)]).fetchone()
#    if proj:
#        return render_template('edit.html', p=proj, title="Edit: " + proj[2], unpublished=True)
#    else:
#        return redirect(url_for('index'))
  
@app.route('/save', methods=['POST'])
def save_edit_p():
    if not session.get('employer'):
        return jsonify({'ok': False, 'errors':['You are not employer']})
    db = get_db()
    try:
        request.form['max_people'] > 3
        max_ = request.form['max_people']
    except:
        max_ = 1
    db.execute("update tasks set login = ?, title = ?, description = ?, content = ?, date = ?, deadline = ?, max_people = ?, subject = ? where id = ?",
    [session['login'], request.form['title'],request.form['description'],request.form['content'],time.strftime("%Y-%m-%d"),request.form['deadline'],max_, request.form['subject'], request.form['id']])
    db.commit()
    return jsonify({'ok': True})
    
#app.route('/save_un', methods=['POST'])
#def save_edit_un():
#    if not session.get('editor'):
#        return jsonify({'ok': False, 'errors':['You are not editor']})
#    db = get_db()
#    db.execute("update unpublished_projects set title = ?, description = ?, content = ?, progress = ?, comments = ?, data_last_edit = ? where id = ?",
#    [request.form['title'], request.form['description'], request.form['content'], request.form['progress'], request.form['comments'], time.strftime("%d.%m.%Y"),request.form['id']])
#    db.commit()
#    return jsonify({'ok': True})

@app.route('/my_works')
def my_works():
    if not session.get('employee'):
        return redirect(url_for('index'))
    db = get_db()
    pr = db.execute('select task from works where login = ?', [session['login']])
    #if not pr.fetchone(): return redirect(url_for('index'))
    return render_template('my.html', projects = pr, title="My projects")

@app.route('/page/<int:num>')
def pages(num):
    db = get_db()
    if num <= 1: num = 1; prev = None; title = None
    else: prev = "/page/" + str(num - 1); title = "Page - " + str(num)
    rows = db.execute('select count(*) from tasks').fetchone()[0]
    if app.config['PROJECTS_PER_PAGE']*(num) >= rows: next_ = None
    else: next_ = "/page/" + str(num + 1)
    pr = db.execute('select title, description, id, login, deadline, now_people, max_people from tasks order by id desc limit ? offset ?', [app.config['PROJECTS_PER_PAGE'], app.config['PROJECTS_PER_PAGE']*(num-1)])
    #if not pr.fetchone(): return redirect(url_for('index'))
    return render_template('index.html', projects = pr, title=title, previous = prev, next = next_)


@app.route('/user/<login>')
def user_pages_1(login):
    return user_pages(login, 1)

@app.route('/user/<login>/<int:num>')
def user_pages(login, num):
    db = get_db()
    if num <= 1: num = 1; prev = None; title = "User's tasks"
    else: prev = "/user/" + login + "/" + str(num - 1); title = "Page - " + str(num)
    rows = db.execute('select count(*) from tasks where login = ?', [login]).fetchone()[0]
    if app.config['PROJECTS_PER_PAGE']*(num) >= rows: next_ = None
    else: next_ = "/user/" + login + "/" + str(num + 1)
    pr = db.execute('select title, description, id, login, deadline, now_people, max_people from tasks where login = ? order by id desc limit ? offset ?', [login, app.config['PROJECTS_PER_PAGE'], app.config['PROJECTS_PER_PAGE']*(num-1)])
    return render_template('index.html', projects = pr, title=title, previous = prev, next = next_)



#@app.route('/check_unpublished')
#def check_unpublished_1():
#    return check_unpublished(1)

#@app.route('/check_unpublished/<int:num>')
#def check_unpublished(num):
#    db = get_db()
#    if num <= 1: num = 1; prev = None; title = "Unpublished projects"
#    else: prev = "/check_unpublished/"+str(num - 1); title = "Page - " + str(num)
#    rows = db.execute('select count(*) from unpublished_projects').fetchone()[0]
#    if app.config['PROJECTS_PER_PAGE']*(num) >= rows: next_ = None
#    else: next_ = "/check_unpublished/"+str(num + 1)
#    pr = db.execute('select title, description, id, login from unpublished_projects order by id desc limit ? offset ?', [app.config['PROJECTS_PER_PAGE'], app.config['PROJECTS_PER_PAGE']*(num-1)])
#    return render_template('check_un.html', projects = pr, title=title, previous = prev, next = next_)

#@app.route('/aprove/<int:num>', methods=['GET'])
#def aprove(num):
#    if not session.get('editor'):
#        return jsonify({'ok': False, 'errors':['You are not editor']})
#    db = get_db()
#    db.execute('insert into projects select * from unpublished_projects where id = ?', [num])
#    db.execute('update projects set editor = ? where id = ?',[session['login'], num])
#    db.execute('delete from unpublished_projects where id = ?',  [num])
#    db.commit()
#    return jsonify({'ok': True})
    

@app.route('/del/<int:num>', methods=['GET'])
def del_p(num):
    if not session.get('employer'):
        return jsonify({'ok': False, 'errors':['You are not employer']})
    db = get_db()
    if db.execute('select * from tasks where id = ? and login = ?',  [num, session['login']]).fetchone():
        db.execute('delete from tasks where id = ?',  [num])
        db.execute('delete from works where task = ?',  [num])
        db.commit()
        return jsonify({'ok': True})
    else: 
        return jsonify({'ok': False, 'errors':['I can`t delete']})

@app.route('/work/<int:num>', methods=['GET'])
def save_work(num):
    if not session.get('employee'):
        return jsonify({'ok': False, 'errors':['You are not employee']})
    db = get_db()
    task = db.execute('select max_people, now_people from tasks where id = ?',  [num]).fetchone()
    try: k = int(task[0])
    except: k = 1
    if task and k > task[1] and not db.execute('select * from works where task = ? and login = ?',  [num, session['login']]).fetchone():
        db.execute("update tasks set now_people = ? where id = ?", [task[1]+1, num])
        db.execute("insert into works (login, content, task) values (?, ?, ?)", [session['login'], "", num])
        db.commit()
        return jsonify({'ok': True})
    else:
        return jsonify({'ok': False, 'errors':['I can`t give you this task']})

#@app.route('/del_un/<int:num>', methods=['GET'])
#def del_un(num):
#    if not session.get('editor'):
#        return jsonify({'ok': False, 'errors':['You are not editor']})
#    db = get_db()
#    db.execute('delete from unpublished_projects where id = ?',  [num])
#    db.commit()
#    return jsonify({'ok': True})
    
@app.route('/profile/<login>')
def profile(login):
    db = get_db()
    p = db.execute('select * from users where login = ?',  [login]).fetchone()
    db.commit()
    return render_template('profile.html', p = p, title="User`s profile")

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8080,debug=True)