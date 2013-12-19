# Copyright (C) 2012-2013 Pablo Oliveira <pablo@sifflez.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from flask import Flask, flash, redirect,\
    url_for, session, g

from functools import wraps
from database import connect_db, query_db

from tigergrader.config import cfg

app = Flask(__name__)
app.config.update(cfg)


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
