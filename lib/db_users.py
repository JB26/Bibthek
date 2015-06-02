"""Operatons on the users db"""
from passlib.hash import pbkdf2_sha512
from datetime import datetime
import re
import random
import string

import lib.db_sql as db_sql

def add_user(username, password, email, session_id):
    """Add a new user"""
    cursor, conn = db_sql.connect('users.db')
    p_re = re.compile('[A-Z-+_0-9]+', re.IGNORECASE)
    m_re = p_re.match(username)
    if m_re == None:
        return '"' + username[0] + '" not allowed in the username'
    elif m_re.group() != username:
        return '"' + username[m_re.span()[1]] + '" not allowed in the username'
    cursor.execute("SELECT * FROM users WHERE username = ?", (username, ))
    if cursor.fetchone() != None:
        return "Username already exists"
    sql = "INSERT INTO users VALUES (?,?,?,?,?,?,?)"
    cursor.execute(sql, (username, pbkdf2_sha512.encrypt(password),
                         datetime.now(), '', email, 'private', [session_id], ))
    conn.commit()
    conn.close()
    db_sql.init_books(username)
    return '0'

def login(username, password, session_id):
    """Login"""
    user = user_by_name(username)
    if user != None and pbkdf2_sha512.verify(password, user['password']):
        if session_id != None:
            cursor, conn = db_sql.connect('users.db')
            session_ids = [session_id] + user['session_ids']
            sql = ("UPDATE users SET session_ids = ? WHERE username = ?")
            cursor.execute(sql, (session_ids, username, ))
            conn.commit()
            conn.close()
        return True
    else:
        return False

def logout_all(username):
    """Logout all sessions"""
    cursor, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET session_ids = ? WHERE username = ?")
    cursor.execute(sql, ([], username, ))
    conn.commit()
    conn.close()

def user_by_name(username):
    """Get userdata with the username"""
    cursor, conn = db_sql.connect('users.db')
    cursor.execute("SELECT * FROM users WHERE username = ?", (username, ))
    temp = cursor.fetchone()
    if temp != None:
        user = dict(temp)
    else:
        user = None
    conn.close()
    return user

def user_by_session(session_id):
    """Get userdata with the session ID"""
    cursor, conn = db_sql.connect('users.db')
    sql = "SELECT * FROM users WHERE session_ids LIKE ?"
    cursor.execute(sql, ('%"' + session_id + '"%', ))
    temp = cursor.fetchone()
    if temp != None:
        user = dict(temp)
    else:
        user = None
    conn.close()
    return user

def change_pw(username, password_old, password_new):
    """Change the user password"""
    user = user_by_name(username)
    if pbkdf2_sha512.verify(password_old, user['password']):
        cursor, conn = db_sql.connect('users.db')
        sql = ("UPDATE users SET password = ? WHERE username = ?")
        cursor.execute(sql, (pbkdf2_sha512.encrypt(password_new), username, ))
        conn.commit()
        conn.close()
        return "0"
    else:
        return "Wrong password"

def reset_pw(username):
    """Reset a password"""
    password_new = ''.join(random.SystemRandom().
                           choice(string.ascii_uppercase + string.digits)
                           for _ in range(6))
    cursor, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET password = ? WHERE username = ?")
    cursor.execute(sql, (pbkdf2_sha512.encrypt(password_new), username, ))
    conn.commit()
    conn.close()
    return password_new

def change_email(username, email):
    """Change email"""
    cursor, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET email = ? WHERE username = ?")
    cursor.execute(sql, (email, username, ))
    conn.commit()
    conn.close()

def user_del(username):
    """Delete a user"""
    cursor, conn = db_sql.connect('users.db')
    sql = ("DELETE FROM users WHERE username = ?")
    cursor.execute(sql, (username, ))
    conn.commit()
    conn.close()

def chg_role(username, role):
    """Change a users role"""
    cursor, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET role = ? WHERE username = ?")
    cursor.execute(sql, (role, username, ))
    conn.commit()
    conn.close()

def privacy(username, status):
    """Change a users privacy setting"""
    cursor, conn = db_sql.connect('users.db')
    sql = ("UPDATE users SET privacy = ? WHERE username = ?")
    cursor.execute(sql, (status, username, ))
    conn.commit()
    conn.close()

def user_list():
    """Return a list with all users"""
    cursor, conn = db_sql.connect('users.db')
    sql = ("SELECT * FROM users ORDER BY username")
    cursor.execute(sql)
    data = [dict(x) for x in cursor.fetchall()]
    conn.close()
    return data
