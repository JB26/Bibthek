"""Init and connect db's"""
import json
import sqlite3
import configparser
CONFIG = configparser.ConfigParser()
CONFIG.read('app.conf')

def connect(db):
    """Connect to db"""
    if db == 'books.db':
        filename = CONFIG['Databases']['path_books_db'][1:-1]
    elif db == 'users.db':
        filename = CONFIG['Databases']['path_users_db'][1:-1]
    conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    sqlite3.register_adapter(list, json.dumps)
    sqlite3.register_converter("list", lambda x: json.loads(x.decode('utf-8')))
    cursor = conn.cursor()
    return cursor, conn

def init_users():
    """Init db users"""
    cursor, conn = connect('users.db')
    cursor.execute('''create table if not exists users(username text,
                      password text, reg_date timestamp, role text, email text,
                      privacy text, session_ids list)''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS username_idx ON
                      users(username)''')
    conn.close()

def init_books(username):
    """Init db books"""
    cursor, conn = connect('books.db')
    sql = ("create table if not exists " + username +
           '''(authors list, description text, release_date text, genre list,
               isbn text, series text, order_nr text, pages text,
               language text, title text, front text, publisher text,
               add_date text, shelf text, type text, colorist list,
               artist list, cover_artist list, narrator list, form text,
               reading_stats list, read_count INTEGER, series_complete INTEGER,
               _id INTEGER primary key autoincrement not null)''')
    cursor.execute(sql)
    conn.close()
