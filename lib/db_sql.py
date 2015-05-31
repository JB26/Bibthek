from passlib.hash import pbkdf2_sha512
from datetime import datetime
import re
import random
import string
from collections import Counter
import json
import sqlite3
import itertools
import operator
from copy import copy

from lib.sort_data import sorted_series, sorted_titles, sorted_shelfs
from lib.sort_data import sorted_apg
from lib.variables import name_fields, dbnames

def connect(filename):
    conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    sqlite3.register_adapter(list, json.dumps)
    sqlite3.register_converter("list", lambda x: json.loads(x.decode('utf-8')))
    c = conn.cursor()
    return c, conn

def init_users():
    c, conn = connect('users.db')
    c.execute('''create table if not exists users(username text, password text,
                 reg_date timestamp, role text, email text, privacy text,
                 session_ids list)''')
    c.execute('''CREATE INDEX IF NOT EXISTS username_idx ON users(username)''')

    conn.close()

def init_books(username):
    c, conn = connect('books.db')
    sql = ("create table if not exists " + username +
           '''(authors list, description text, release_date text, genre list,
               isbn text, series text, order_nr text, pages text,
               language text, title text, front text, publisher text,
               add_date text, shelf text, type text, colorist list,
               artist list, cover_artist list, narrator list, form text,
               reading_stats list, read_count INTEGER, series_complete INTEGER,
               _id INTEGER primary key autoincrement not null)''')
    c.execute(sql)

    conn.close()
