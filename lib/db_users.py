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
import lib.db_sql as db_sql

def add_user(username, password, email, session_id):
    c, conn = db_sql.connect('users.db')
    p = re.compile('[A-Z-+_0-9]+', re.IGNORECASE)
    m = p.match(username)
    if m == None:
        return '"' + username[0] + '" not allowed in the username'
    elif m.group() != username:
        return '"' + username[m.span()[1]] + '" not allowed in the username'
    c.execute("SELECT * FROM users WHERE username = ?", (username, ))
    if c.fetchone() != None:
        return "Username already exists"
    sql = "INSERT INTO users VALUES (?,?,?,?,?,?,?)"
    c.execute(sql, (username, pbkdf2_sha512.encrypt(password),
                    datetime.now(), '', email, 'private', [], ))
    conn.commit()
    conn.close()
    init_books(username)
    return '0'

def login(username, password, session_id):
    user = user_by_name(username)
    if user != None and pbkdf2_sha512.verify(password, user['password']):
        if session_id != None:
            c, conn = db_sql.connect('users.db')
            session_ids = [session_id] + user['session_ids']
            sql = ("UPDATE users SET session_ids = ? WHERE username = ?")
            c.execute(sql, (session_ids, username, ))
            conn.commit()
            conn.close()
        return True
    else:
        return False

def logout_all(username):
    c, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET session_ids = ? WHERE username = ?")
    c.execute(sql, ([], username, ))
    conn.commit()
    conn.close()

def user_by_name(username):
    c, conn = db_sql.connect('users.db')
    c.execute("SELECT * FROM users WHERE username = ?", (username, ))
    temp = c.fetchone()
    if temp != None:
        user = dict(temp)
    else:
        user = None
    conn.close()
    return user
        

def change_pw(username, password_old, password_new):
    user = user_by_name(username)
    if pbkdf2_sha512.verify(password_old, user['password']):
        c, conn = db_sql.connect('users.db')
        sql = ("UPDATE users SET password = ? WHERE username = ?")
        c.execute(sql, (pbkdf2_sha512.encrypt(password_new), username, ))
        conn.commit()
        conn.close()
        return "0"
    else:
        return "Wrong password"

def reset_pw(username):
    password_new = ''.join(random.SystemRandom().
                           choice(string.ascii_uppercase + string.digits)
                           for _ in range(6))
    c, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET password = ? WHERE username = ?")
    c.execute(sql, (pbkdf2_sha512.encrypt(password_new), username, ))
    conn.commit()
    conn.close()
    return password_new

def change_email(username, email):
    c, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET email = ? WHERE username = ?")
    c.execute(sql, (email, username, ))
    conn.commit()
    conn.close()

def user_del(username):
    c, conn = db_sql.connect('users.db')
    sql = ("DELETE FROM users WHERE username = ?")
    c.execute(sql, (username, ))
    conn.commit()
    conn.close()

def role(username, role):
    c, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET role = ? WHERE username = ?")
    c.execute(sql, (role, username, ))
    conn.commit()
    conn.close()

def privacy(username, status):
    c, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET privacy = ? WHERE username = ?")
    c.execute(sql, (status, username, ))
    conn.commit()
    conn.close()

    
def user_list():
    c, conn = db_sql.connect('users.db')
    sql = ("SELECT * FROM users ORDER BY username")
    c.execute(sql)
    conn.close()
    return [ dict(x) for x in c.fetchall() ]
