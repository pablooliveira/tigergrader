from tigergrader import app, login_required, get_active_modules, \
    GraderConfiguration

from flask import flash, redirect, render_template, \
    request, url_for, session, g, jsonify

from werkzeug.security import generate_password_hash, \
    check_password_hash


import sqlite3
import time
import json
import uuid
import re
import os

from grader import grade
from database import query_db

is_email = re.compile(r"[^@]+@[^@]+\.[^@]+")


@app.route('/')
@login_required
def index():
    active = app.config["MODULES"]

    grades_raw = query_db('select test,grade from grades where user = ?',
                          [session["username"]])

    grades = []
    for module in active:
        best_grade = max([gr["grade"] for gr in grades_raw
                          if gr["test"] == module] + [0])
        grades.append(dict(test=module, grade=best_grade))

    return render_template('dashboard.html',
                           user=session["username"],
                           grades=grades)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if GraderConfiguration()["registration"] != "open":
        flash("Registration is currently closed")
        return redirect(url_for('login'))

    if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            emails = request.form['emails']

            password_hash = generate_password_hash(password)

            notok = False

            if len(password) < 8:
                flash('Password must be at least 8 characters long')
                notok = True
            if len(username) < 3:
                flash('Username must be at least 3 characters long')
                notok = True
            if not re.match("^[A-Za-z0-9_-]*$", username):
                flash('Username can only contain letters, \
                       underscores and dashes')
                notok = True
            if username == app.config['ADMIN_USERNAME']:
                flash('Account already exists')
                notok = True

            emails_list = emails.split(",")
            if not emails_list:
                flash('At least one email must be provided')
                notok = True

            for e in emails_list:
                # The RE check used is much too simple, but
                # catches most of the mistakes
                if not is_email.match(e):
                    flash('Emails addresses are not correct')
                    notok = True

            if notok:
                return redirect(url_for('register'))

            try:
                g.db.execute("INSERT INTO users VALUES(?,?,?)",
                             (username, password_hash, emails))
                g.db.commit()
                flash('Account successfully created')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Account already exists')
                return redirect(url_for('register'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        result = query_db("select password from users where user == ?",
                          args=[username], one=True)

        if result and check_password_hash(result["password"], password):
            session['username'] = request.form['username']
            flash('You were successfully logged in')
            return redirect(url_for('index'))
        else:
            error = "Invalid Credentials"
    return render_template('login.html', error=error)


@app.route('/handout/<test>', methods=['GET'])
@login_required
def handout(test):
    if test not in app.config["MODULES"]:
        flash("Module does not seem to exist")
        return redirect(url_for('index'))

    grades_raw = query_db('select * from grades where test = ? and user = ?',
                          [test, session["username"]])

    best_grade = max([g["grade"]
                     for g in grades_raw if g["test"] == test] + [0])

    with file(os.path.join(app.config["MODULE_FOLDER"],
              test, test + ".html")) as f:
        return render_template('handout.html',
                               best_grade=best_grade,
                               grades=grades_raw[::-1],
                               test=test,
                               user=session["username"],
                               module_content=f.read().decode('utf-8'))


@app.route('/report/<test>', methods=['GET'])
@app.route('/report/<test>/<report>', methods=['GET'])
@login_required
def report(test, report=None):

    if not report:
        grades = query_db('select grade, report from grades where test = ? \
                           and user = ?',
                          [test, session["username"]])
    else:
        grades = query_db('select grade, report from grades where test = ? \
                           and user = ? and report = ?',
                          [test, session["username"], report])

    if not grades:
        flash("You have not yet submitted any work for this handout")
        return redirect(url_for('handout', test=test))

    grades = grades[-1]

    report_id = grades["report"]
    report = query_db('select detail from reports where id = ?',
                      [report_id])

    tests = json.loads(report[-1]["detail"])

    return render_template('grades.html',
                           grade=grades["grade"],
                           tests=tests,
                           test=test)


@app.route('/waitfor/<task>')
def waitfor(task):
    result = grade.AsyncResult(task)
    while(not result.ready()):
        time.sleep(1)
    return jsonify(task=task)


@app.route('/submit/<test>', methods=['GET', 'POST'])
@login_required
def submit(test):

    if test not in get_active_modules():
        flash("Module does not seem to exist or is inactive.")
        return redirect(url_for('index'))

    f = request.files['file']
    if f and request.method == 'POST':
        filename = str(uuid.uuid1())
        dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(dest)
        task = grade.delay(os.path.abspath(dest), test, session["username"])

        return render_template('waiting.html', test=test, task=task,
                               timeout=app.config['SUBMISSION_TIMEOUT'])
    else:
        return render_template('upload.html', test=test)


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))
