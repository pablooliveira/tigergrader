from flask import Flask, flash, redirect,\
    url_for, session, g

from functools import wraps
from database import connect_db, query_db

app = Flask(__name__)
app.config.from_envvar('TIGERGRADER_SETTINGS')


class GraderConfiguration():

    def __setitem__(self, k, v):
        g.db.execute('replace into configuration values (?, ?)', (k, v))
        g.db.commit()

    def __getitem__(self, k):
        v = query_db('select value from configuration where key == ?', [k])
        if v and "value" in v[0]:
            return v[0]["value"]


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            flash('You need to log in')
            return redirect(url_for('login'))

        elif session["username"] == app.config["ADMIN_USERNAME"]:
            return redirect(url_for('admin'))

        return f(*args, **kwargs)
    return decorated_function


def get_active_modules():
    conf = GraderConfiguration()
    active_modules = conf["active_modules"]
    if active_modules:
        active_modules = active_modules.split(",")
    else:
        active_modules = []
    return active_modules


import tigergrader.admin
import tigergrader.student
