#!/usr/bin/env python
import sys
from werkzeug.security import generate_password_hash
from tigergrader.database import connect_db, init_db
from flask import Config
cfg = Config('.')
cfg.from_envvar('TIGERGRADER_SETTINGS')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print >>sys.stderr, "usage: create-admin.py ADMIN_EMAIL ADMIN_PASSWORD"
        sys.exit(1)

    username = cfg["ADMIN_USERNAME"]
    emails = sys.argv[1]
    password = sys.argv[2]

    password_hash = generate_password_hash(password)

    db = connect_db()
    init_db()
    db.execute("INSERT INTO users VALUES(?,?,?)",
               (username, password_hash, emails))
    db.commit()
    db.close()
