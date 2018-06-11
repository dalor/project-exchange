from flask import Flask, g
import sqlite3
import sys

app = Flask(__name__)

def connect_db(database):
    rv = sqlite3.connect(database)
    rv.row_factory = sqlite3.Row
    return rv

def get_db(database):
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db(database)
    return g.sqlite_db

def init_db(database, scheme):
    with app.app_context():
        db = get_db(database)
        with app.open_resource(scheme, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

#args = sys.argv
#init_db(args[1],args[2])
init_db('db.db','db.sql')

