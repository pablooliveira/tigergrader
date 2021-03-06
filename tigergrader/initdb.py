#!/usr/bin/env python
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

from contextlib import closing
import os
import sqlite3
import sys
from werkzeug.security import generate_password_hash
from tigergrader.database import connect_db
from tigergrader.config import cfg


def init_db():
    install_path = os.path.dirname(os.path.realpath(__file__))
    with closing(connect_db()) as db:
        with open(os.path.join(install_path, "schema.sql")) as f:
            db.cursor().executescript(f.read())
        db.commit()


def create_user(username, emails, password):
    password_hash = generate_password_hash(password)
    db = connect_db()
    try:
        db.execute("INSERT INTO users VALUES(?,?,?)",
                   (username, password_hash, emails))
        db.commit()
    except sqlite3.IntegrityError:
        print >>sys.stderr, "Account already exists"
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >>sys.stderr, "usage: create-admin.py ADMIN_EMAIL ADMIN_PASSWORD"
        sys.exit(1)

    username = cfg["ADMIN_USERNAME"]
    emails = sys.argv[1]
    password = sys.argv[2]

    init_db()

    create_user(username, emails, password)
