from contextlib import closing
import os
import sqlite3
from flask import Config, g
cfg = Config('.')
cfg.from_envvar('TIGERGRADER_SETTINGS')


def query_db(query, args=(), one=False, db=None):
    if not db:
        db = g.db
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


def connect_db():
    return sqlite3.connect(cfg["DATABASE"])


def init_db():
    install_path = os.path.dirname(os.path.realpath(__file__))
    with closing(connect_db()) as db:
        with open(os.path.join(install_path, "schema.sql")) as f:
            db.cursor().executescript(f.read())
        db.commit()
