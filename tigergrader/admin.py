from tigergrader import app, GraderConfiguration, get_active_modules
from functools import wraps
from flask import flash, redirect, render_template, \
    request, url_for, session, Response

from plagiarism import check_plagiarism, read_check_file
import os

from database import query_db


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session \
                or session["username"] != app.config["ADMIN_USERNAME"]:
            flash('Administrative account required')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/archive/<filename>', methods=['GET'])
@admin_required
def archive(filename):
    fpath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print "FILE IS", fpath
    if os.path.isfile(fpath):
        with open(fpath) as f:
            return Response(f.read(), mimetype='application/zip')
    else:
        flash('Submission not found')
        return redirect(url_for('admin'))


@app.route('/plagiarism/<test>')
@admin_required
def plagiarism(test):
    if test not in app.config["MODULES"]:
        flash("Module does not seem to exist")
        return redirect(url_for('index'))

    report = check_plagiarism(test)
    return render_template('plagiarism.html',
                           user=session["username"],
                           test=test,
                           plagiarism=report)


@app.route('/compare/<test>/<u1>/<u2>/')
@admin_required
def compare(test, u1, u2):
    if test not in app.config["MODULES"]:
        flash("Module does not seem to exist")
        return redirect(url_for('index'))

    d1 = read_check_file(test, u1)
    d2 = read_check_file(test, u2)
    return render_template('compare.html',
                           user=session["username"],
                           test=test,
                           d1=d1,
                           d2=d2)


@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    conf = GraderConfiguration()
    modules = app.config["MODULES"]

    if request.method == 'POST':
        if "_registration" in request.form:
            conf["registration"] = "open"
        else:
            conf["registration"] = "closed"
        active_modules = []
        for m in modules:
            if m in request.form:
                active_modules.append(m)
        conf["active_modules"] = ",".join(active_modules)
        flash("Active modules updated")
        return redirect(url_for('admin'))
    else:
        registration_active = conf["registration"] == "open"
        active_modules = get_active_modules()
        module_active = dict([(m, m in active_modules) for m in modules])

        all_grades_raw = query_db('select * from (select test, user, \
                timestamp, grade, upload from grades \
                order by grade ASC, timestamp DESC) \
                as tmp group by test, user')

        groups = []
        emails = []
        for u in query_db('select user, emails from users order by user'):
            if u != app.config["ADMIN_USERNAME"]:
                groups.append(u["user"])
                emails.append(u["emails"])

        all_grades = dict([(g, {}) for g in groups])
        for g in all_grades_raw:
            if g["user"] not in groups:
                continue
            all_grades[g["user"]][g["test"]] = dict(grade=g["grade"],
                                                    timestamp=g["timestamp"],
                                                    upload=g["upload"])

        return render_template('admin.html',
                               all_grades=all_grades,
                               groups_emails=zip(groups, emails),
                               modules=modules,
                               module_active=module_active,
                               registration_active=registration_active,
                               user=session["username"])
