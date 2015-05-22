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

def connect(filename='books.db'):
    conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    sqlite3.register_adapter(list, json.dumps)
    sqlite3.register_converter("list", lambda x: json.loads(x.decode('utf-8')))
    c = conn.cursor()
    return c, conn

def init_users():
    c, conn = connect(filename='users.db')
    c.execute('''create table if not exists users(username text, password text,
                 reg_date timestamp, role text, email text, privacy text,
                 session_ids list)''')
    c.execute('''CREATE INDEX IF NOT EXISTS username_idx ON users(username)''')

    conn.close()

def init_books(username):
    c, conn = connect(filename='books.db')
    sql = ("create table if not exists " + username +
           '''(authors list, description text, release_date text, genre list,
               isbn text, series text, order_nr text, pages text, language text,
               title text, front text, publisher text, binding text,
               add_date text, shelf text, type text, colorist list,
               artist list, cover_artist list, form text, reading_stats list,
               read_count INTEGER, series_complete INTEGER,
               _id INTEGER primary key autoincrement not null)''')
    c.execute(sql)

    conn.close()

def insert_new_book(username, data):
    c, conn = connect()
    sql = ("INSERT INTO " + username + " (" + ", ".join(dbnames) +
           ") VALUES (" + ", ".join(['?']*len(dbnames)) + ")")
    temp_list = []
    for key in dbnames:
        temp_list.append(data[key])
    c.execute(sql, tuple(temp_list))
    conn.commit()
    conn.close()
    return c.lastrowid

def insert_many_new(username, data):
    c, conn = connect()
    sql = ("INSERT INTO " + username + " (" + ", ".join(dbnames) +
           ") VALUES (" + ", ".join(['?']*len(dbnames)) + ")")

    insert_data = []
    for x in data:
        x = str_to_array(x)
        temp_list = []
        for key in dbnames:
            temp_list.append(x[key])
        insert_data.append(tuple(temp_list))
    c.executemany(sql, insert_data)
    conn.commit()
    conn.close()
    return

def update_book(username, book_id, data):
    c, conn = connect()
    keys = list(data.keys())
    sql = ("UPDATE " + username + " SET " + " = ?, ".join(keys) +
           " = ? WHERE _id = ?")
    temp_list = []
    for key in keys:
        temp_list.append(data[key])
    temp_list.append(book_id)
    c.execute(sql, tuple(temp_list))
    conn.commit()
    conn.close()
    return c.lastrowid

def array_to_str(data):
    for field in name_fields:
            if field in data:
                data[field] = ' & '.join(data[field])
    if 'genre' in data:
        data['genre'] = ', '.join(data['genre'])
    return data

def str_to_array(data):
    for field in name_fields:
            if field in data:
                data[field] = data[field].split(' & ')
    if 'genre' in data:
        data['genre'] = data['genre'].split(', ')
    return data

def remove_empty_field(data, warning):
    data_temp = None
    for row in data:
        if row['_id'] == '':
            data_temp = row
            row['_id'] = warning
            row['empty_field'] = True
        else:
            row['empty_field'] = False
        row['sub_items'] = True
    data = [x for x in data if x['_id'] != warning]
    return data, data_temp

def sort_insert_empty(data_temp, data):
    if data_temp != None:
            data_temp['books'] = sorted_titles(data_temp['books'], 'title')
            data.append(data_temp)
    return data

def query_builder(filters, shelf):
    filter_list = filters.split('+')
    if 'stat_Read' in filter_list:
        query = " AND read_count > 0"
    elif 'stat_Unread' in filter_list:
        query = " AND read_count = 0"
    else:
        query = ""
    if 'form_Physical' in filter_list:
        query += " AND form = 'Physical'"
    elif 'form_Digital' in filter_list:
        query += " AND form = 'Digital'"
    elif 'form_Borrowed' in filter_list:
        query += " AND form = 'Borrowed'"

    paras = {}
    for _filter in filter_list:
        if len(_filter) > 5:
            if _filter[0:5] == 'lang_':
                query += " AND language=:lang"
                paras['lang'] = _filter[5:]
            if  _filter[0:5] == 'bind_':
                query += " AND binding=:bind"
                paras['bind'] = _filter[5:]

    if shelf == 'Not shelfed':
        query += " AND shelf = ''"
    elif shelf != 'All':
        query += " AND shelf=:shelf"
        paras['shelf'] = shelf
    if query != '':
        query = " WHERE" + query[4:]

    return query, paras

def update(username, data):
    book_id = data['book_id']
    del data['book_id']
    data = str_to_array(data)
    if 'start_date' in data:
        data['reading_stats'] = []
        if not isinstance(data['start_date'], list):
            data['start_date'] = [data['start_date']]
        if not isinstance(data['finish_date'], list):
            data['finish_date'] = [data['finish_date']]
        temp = [False] * len(data['start_date'])
        data['read_count'] = len(data['start_date'])
        if 'abdoned' in data:
            if not isinstance(data['abdoned'], list):
                data['abdoned'] = [data['abdoned']]
            for i in data['abdoned']:
                temp[int(i)-1] = True
        data['abdoned'] = temp
        
        for start, finish, abdoned in zip(data['start_date'],
                                          data['finish_date'],
                                          data['abdoned']):
            data['reading_stats'].append({'start_date' : start,
                                          'finish_date' : finish,
                                          'abdoned' : abdoned})
        del data['start_date']
        del data['finish_date']
        del data['abdoned']
    if book_id == 'new_book':
        book_id = insert_new_book(username, data)
    else:
        update_book(username, book_id, data)
    return book_id

def change_field(username, edit, old_name, new_name):
    c, conn = connect()
    if edit == 'series':
        sql = ("UPDATE " + username + " SET series = ? WHERE series = ?")
        c.execute(sql,(new_name, old_name, ))
    elif edit in name_fields:
        sql = ("SELECT " + edit + ", _id FROM " + username + " WHERE " + edit +
               " LIKE ?")
        c.execute(sql, ('%"' + old_name + '"%', ))
        sql  = ("UPDATE " + username + " SET " + edit + " = ? WHERE _id = ?")
        for x in c.fetchall():
            if len(x[edit]) == 1:
                c.execute(sql, ([new_name], x['_id'], ))
            else:
                x_new = []
                for name in x[edit]:
                    if name == old_name:
                        x_new.append(new_name)
                    else:
                        x_new.append(name)

                c.execute(sql, (x_new, x['_id'], ))
    conn.commit()
    conn.close()

def star_series(username, series, status):
    c, conn = connect()
    sql = ("UPDATE " + username + " SET series_complete = ? WHERE series = ?")
    if status == 'star':
        c.execute(sql, (0, series, ))
    else:
        c.execute(sql, (1, series, ))
    conn.commit()
    conn.close()

def get_by_id(username, book_id, field = None):
    c, conn = connect()
    if field == None:
        sql = "SELECT * FROM " + username + " WHERE _id = ?"
        c.execute(sql, (book_id,) )
    else:
        sql = "SELECT " + field + " FROM " + username + " WHERE _id = ?"
        c.execute(sql, (book_id,))
    data = array_to_str(dict(c.fetchone()))
    return data

def get_all(username):
    c, conn = connect()
    c.execute("SELECT * FROM " + username)
    data = [ array_to_str(dict(x)) for x in c.fetchall() ]
    conn.close()
    return data

def aggregate_items(username, group_by, get_fields, shelf, _filter,
                    array=False):

    c, conn = connect()
    sql = ("SELECT " + group_by + ", " +
           ", ".join(get_fields) + " FROM " + username)
    query, paras = query_builder(_filter, shelf)
    c.execute(sql + query, paras)
    data = [ dict(x) for x in c.fetchall() ]
    data_temp = []
    if array:
        for row in data:
            temp_field = row[group_by][1:]
            row[group_by] = row[group_by][0]
            for x in temp_field:
                data_temp.append(copy(row))
                data_temp[-1][group_by] = x
        data += data_temp
    data = sorted(data, key=operator.itemgetter(group_by))
    list1 = []
    for key, items in itertools.groupby(data, operator.itemgetter(group_by)):
        list1.append({'_id': key, 'books': list(items)})
    return list1

def series(username, shelf, variant, _filter):
    order_by = variant.split('_')[1]
    if order_by == 'year':
        order_by = 'release_date AS order_nr'
    elif order_by == 'order':
        order_by = 'order_nr'
    data = aggregate_items(username, 'series',
                           ["title", "_id", order_by, "series_complete"],
                           shelf, _filter)
    data, data_temp = remove_empty_field(data, 'Not in a series')
    if variant.split('_')[0] == 'variant1' and data_temp != None:
        for row in data_temp['books']:
            data.append({'_id' : row['title'],
                         'sub_items' : False,
                         'books' : {'_id' : row['_id']}})
        data = sorted_series(data, variant)
    else:
        data = sorted_series(data, variant)
        data = sort_insert_empty(data_temp, data)
    return data

def author_and_more(username, sortby, shelf, variant, _filter):
    if sortby in name_fields or sortby == 'genre':
        array = True
    else:
        array = False
    if variant == 'year':
        data = aggregate_items(
            username, sortby,
            ["title", "_id", "release_date AS order_nr"],
            shelf, _filter, array
            )
        sort_by_order = True
    elif variant == 'title':
        data = aggregate_items(
            username, sortby,
            ["title", "_id"],
            shelf, _filter, array
            )
        sort_by_order = False
    data, data_temp = remove_empty_field(data, 'No ' + sortby)
    data = sorted_apg(data, sort_by_order, sortby)
    data = sort_insert_empty(data_temp, data)
    return data

def titles(username, shelf, variant, _filter):
    c, conn = connect()
    sql = ("SELECT title, release_date, pages, _id FROM " + username)
    query, paras = query_builder(_filter, shelf)
    c.execute(sql + query, paras)
    data_temp = [ dict(x) for x in c.fetchall() ]
    data = []
    for row in data_temp:
        temp = {'_id' : row['title'],
                'sub_items' : False,
                'books' : {'_id' : row['_id']}}
        if variant == 'year':
            temp['order_nr'] = row['release_date']
        elif variant == 'pages':
            temp['order_nr'] = row['pages']
        data.append(temp)
    return sorted_titles(data, '_id', variant)

def covers(username, shelf, _filter):
    c, conn = connect()
    sql = ("SELECT front, _id FROM " + username)
    query, paras = query_builder(_filter, shelf)
    c.execute(sql + query, paras)
    data_temp = [ dict(x) for x in c.fetchall() ]
    data = {}
    for row in data_temp:
        data[str(row["_id"])] = row["front"]
    return data

def statistic_date(username, shelf, _filter, _type):
    _type = _type.split('#')
    c, conn = connect()
    query, paras = query_builder(_filter, shelf)
    if _type[0] in ['release_date', 'add_date']:
        sql = ("SELECT " + _type[0] + " FROM " + username)
    else:
        sql = ("SELECT reading_stats FROM " + username)
    c.execute(sql + query, paras)
    data_temp =  [ dict(x) for x in c.fetchall() ]
    data = []
    if len(_type) == 1:
        for row in data_temp:
            if _type[0] in ['release_date', 'add_date']:
                if row[_type[0]]  != '':
                    data.append(row[_type[0]][0:4])
            else:
                for row2 in row["reading_stats"]:
                    if row2[_type[0]]  != '':
                        data.append(row2[_type[0]][0:4])
    elif len(_type) == 2:
        for row in data_temp:
            if _type[0] in ['release_date', 'add_date']:
                if row[_type[0]]  != '' and row[_type[0]][0:4] == _type[1]:
                    data.append(row[_type[0]][5:7])
            else:
                for row2 in row["reading_stats"]:
                    if (row2[_type[0]]  != '' and
                        row2[_type[0]][0:4] == _type[1]):
                        data.append(row2[_type[0]][5:7])
    data = Counter(data)
    labels = sorted(list(data))
    data = [ data[x] for x in labels  ]
    if labels != [] and labels[0] == "":
        labels[0] = "Unknown"
    return labels, data

def statistic_pages_read(username, shelf, _filter, _type):
    _type = _type.split('#')
    c, conn = connect()
    query, paras = query_builder(_filter, shelf)
    sql = ("SELECT reading_stats, pages FROM " + username)
    c.execute(sql + query, paras)
    data_temp = [ dict(x) for x in c.fetchall() ]
    data = []
    for row in data_temp:
        for row2 in row["reading_stats"]:
            if row2["finish_date"]  != '' and row2["start_date"]  != '':
                data.append([row2["start_date"], row2["finish_date"],
                             row["pages"]])
    data_temp = {}
    if len(_type) == 1:
        for row in data:
            i = 0
            while len(row[2]) > i and row[2][i].isdigit():
                i = i+1
            if i > 0:
                row[0] = int(row[0][0:4])
                row[1] = int(row[1][0:4])
                row[2] = int(row[2][0:i])
                if row[1]-row[0]+1 > 0:
                    for i in range(row[0], row[1]+1):
                        if i in data_temp:
                            data_temp[i] = (data_temp[i] +
                                            row[2]/(row[1]-row[0]+1))
                        else:
                            data_temp[i] = row[2]/(row[1]-row[0]+1)
    elif len(_type) == 2:
        for row in data:
            i = 0
            while len(row[2]) > i and row[2][i].isdigit():
                i = i+1
            if i > 0 and (row[0][0:4] == _type[1] or
                          row[1][0:4] == _type[1]):
                row[0] = [int(row[0][0:4]), int(row[0][5:7])]
                row[1] = [int(row[1][0:4]), int(row[1][5:7])]
                row[2] = int(row[2][0:i])
                if row[1][0]-row[0][0]+1 > 1 or (
                        row[1][0]-row[0][0]+1 > 0 and
                        row[1][1]-row[0][1]+1 > 0):
                    if row[0][0] == row[1][0]:
                        i_start = row[0][1]
                        i_end = row[1][1]
                    elif row[0][0] == int(_type[1]):
                        i_start = row[0][1]
                        i_end = 12
                    elif row[1][0] == int(_type[1]):
                        i_start = 1
                        i_end = row[1][1]
                    for i in range(i_start, i_end+1):
                        if i in data_temp:
                            data_temp[i] = (data_temp[i] +
                                            row[2]/(row[1][1]-row[0][1]+1+
                                                    12*(row[1][0]-row[0][0])))
                        else:
                            data_temp[i] = row[2]/(row[1][1]-row[0][1]+1+
                                                    12*(row[1][0]-row[0][0]))
    data = data_temp
    labels = sorted(list(data))
    data = [ data[x] for x in labels  ]
    labels = [ str(x) for x in labels ]
    return labels, data

def statistic_pages_book(username, shelf, _filter):
    c, conn = connect()
    query, paras = query_builder(_filter, shelf)
    sql = ("SELECT pages FROM " + username)
    c.execute(sql + query, paras)
    data_temp = [ dict(x) for x in c.fetchall() ]
    data = []
    for row in data_temp:
        i = 0
        while len(row["pages"]) > i and row["pages"][i].isdigit():
            i = i+1
        if i > 0:
            data.append(round(int(row["pages"][0:i])/100-0.5)*100)
    data = Counter(data)
    labels = sorted(list(data))
    data = [ data[x] for x in labels  ]
    labels = [ str(x) + "-" + str(x+99) for x in labels ]
    return labels, data

def delete_by_id(username, book_id):
    c, conn = connect()
    sql = ("DELETE FROM " + username + " WHERE _id=?")
    c.execute(sql, (book_id, ))
    conn.commit()
    conn.close()

def shelfs(username, _filter):
    query, paras = query_builder(_filter, 'All')
    sql = "SELECT DISTINCT shelf AS _id FROM " + username
    c, conn = connect()
    c.execute(sql + query, paras)
    shelfs = [ dict(x) for x in c.fetchall() ]
    shelfs = sorted_shelfs(shelfs)
    shelfs.insert(0,{'_id' : 'All'})
    for shelf in shelfs:
        shelf['#items'] = count_items(username, shelf['_id'], _filter)
        if shelf['_id'] != '':
            shelf['name'] = shelf['_id']
        else:
            shelf['name'] = 'Not shelfed'
    return shelfs

def autocomplete(username, query, field, array):
    c, conn = connect()
    sql = ("SELECT DISTINCT " + field + " FROM " + username + " WHERE " +
           field + " LIKE ?")
    if array:
        c.execute(sql, ('%"' + query + '%', ))
        ac_list = []
        for x in c.fetchall():
            if len(x[field]) == 1:
                ac_list.append(x[field][0])
            else:
                for name in x[field]:
                    if name[0:len(query)] == query:
                        ac_list.append(name)
        ac_list = {'suggestions' : ac_list}
        
    else:
        c.execute(sql, (query + '%', ))
        ac_list = {'suggestions' : [ x[field] for x in c.fetchall() ]}
    return ac_list

def filter_list(username, shelf, field):
    c, conn = connect()
    sql = "SELECT DISTINCT " + field + " AS '_id' FROM " + username
    if shelf == 'Not shelfed':
        shelf = ''
    if shelf != 'All':
        sql += " WHERE shelf = ?"
        c.execute(sql, (shelf, ))
    else:
        c.execute(sql)

    filter_list = [ dict(x) for x in c.fetchall() ]
    return [ x['_id'] for x in filter_list if x['_id'] != '']

def count_items(username, shelf, _filter):
    c, conn = connect()
    sql = "SELECT COUNT(*) AS items FROM " + username
    query, paras = query_builder(_filter, shelf)
    c.execute(sql + query, paras)
    items = c.fetchone()['items']
    return str(items)

def add_user(username, password, email, session_id):
    c, conn = connect(filename='users.db')
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
            c, conn = connect(filename='users.db')
            session_ids = [session_id] + user['session_ids']
            sql = ("UPDATE users SET session_ids = ? WHERE username = ?")
            c.execute(sql, (session_ids, username, ))
            conn.commit()
            conn.close()
        return True
    else:
        return False

def logout_all(username):
    c, conn = connect(filename='users.db')
    sql = ("UPDATE users SET session_ids = ? WHERE username = ?")
    c.execute(sql, ([], username, ))
    conn.commit()
    conn.close()

def user_by_name(username):
    c, conn = connect(filename='users.db')
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
        c, conn = connect(filename='users.db')
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
    c, conn = connect(filename='users.db')
    sql = ("UPDATE users SET password = ? WHERE username = ?")
    c.execute(sql, (pbkdf2_sha512.encrypt(password_new), username, ))
    conn.commit()
    conn.close()
    return password_new

def change_email(username, email):
    c, conn = connect(filename='users.db')
    sql = ("UPDATE users SET email = ? WHERE username = ?")
    c.execute(sql, (email, username, ))
    conn.commit()
    conn.close()

def user_del(username):
    c, conn = connect(filename='users.db')
    sql = ("DELETE FROM users WHERE username = ?")
    c.execute(sql, (username, ))
    conn.commit()
    conn.close()

def role(username, role):
    c, conn = connect(filename='users.db')
    sql = ("UPDATE users SET role = ? WHERE username = ?")
    c.execute(sql, (role, username, ))
    conn.commit()
    conn.close()

def privacy(username, status):
    c, conn = connect(filename='users.db')
    sql = ("UPDATE users SET privacy = ? WHERE username = ?")
    c.execute(sql, (status, username, ))
    conn.commit()
    conn.close()

    
def user_list():
    c, conn = connect(filename='users.db')
    sql = ("SELECT * FROM users ORDER BY username")
    c.execute(sql)
    return [ dict(x) for x in c.fetchall() ]

def drop(username):
    c, conn = connect()
    sql = ("DELETE FROM " + username)
    c.execute(sql)
    conn.commit()
    conn.close()
