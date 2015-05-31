"""All the db operations for storing and retrieving boog data"""
from collections import Counter
import itertools
import operator
from copy import copy

from lib.sort_data import sorted_series, sorted_titles, sorted_shelfs
from lib.sort_data import sorted_apg
from lib.variables import VARIABLES
import lib.db_sql as db_sql

def insert_new_book(username, data):
    """Make a new db entry"""
    cursor, conn = db_sql.connect('books.db')
    sql = ("INSERT INTO " + username + " (")
    temp_list = []
    for key, value in data.items():
        if key in VARIABLES.dbnames:
            temp_list.append(value)
            sql += key + ", "
    sql = sql[:-2]
    sql += ") VALUES (" + ", ".join(['?']*len(temp_list)) + ")"
    cursor.execute(sql, tuple(temp_list))
    conn.commit()
    conn.close()
    return str(cursor.lastrowid)

def insert_many_new(username, data):
    """Make many new db entrys (when importing books)"""
    cursor, conn = db_sql.connect('books.db')
    keys = list(data[0].keys())
    sql = ("INSERT INTO " + username + " (" + ", ".join(keys) +
           ") VALUES (" + ", ".join(['?']*len(keys)) + ")")

    insert_data = []
    for book in data:
        book = str_to_array(book)
        temp_list = []
        for key in keys:
            temp_list.append(book[key])
        insert_data.append(tuple(temp_list))
    cursor.executemany(sql, insert_data)
    conn.commit()
    conn.close()
    return

def update_book(username, book_id, data):
    """Update book data"""
    cursor, conn = db_sql.connect('books.db')
    keys = list(data.keys())
    sql = ("UPDATE " + username + " SET " + " = ?, ".join(keys) +
           " = ? WHERE _id = ?")
    temp_list = []
    for key in keys:
        temp_list.append(data[key])
    temp_list.append(book_id)
    cursor.execute(sql, tuple(temp_list))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def array_to_str(data):
    """Convert an array to a string"""
    for field in VARIABLES.name_fields:
        if field in data and data[field] != None:
            data[field] = ' & '.join(data[field])
    if 'genre' in data:
        data['genre'] = ', '.join(data['genre'])
    return data

def str_to_array(data):
    """Convert a string to an array"""
    for field in VARIABLES.name_fields:
        if field in data:
            data[field] = data[field].split(' & ')
    if 'genre' in data:
        data['genre'] = data['genre'].split(', ')
    return data

def rearrange_data(data, warning):
    """Put all books where the current main sorting field is empty
    in a separate array (data_temp)
    """
    data_temp = None
    for row in data:
        if row['_id'] == '' or row['_id'] == None:
            data_temp = row
            row['_id'] = warning
            row['empty_field'] = True
        else:
            row['empty_field'] = False
        row['sub_items'] = True
    data = [x for x in data if x['_id'] != warning]
    return data, data_temp

def sort_append_rearranged(data_temp, data):
    """Sort and then append the data_temp array to data"""
    if data_temp != None:
        data_temp['books'] = sorted_titles(data_temp['books'], 'title')
        data.append(data_temp)
    return data

def query_builder(filters, shelf):
    """Build the query according to the activated shelf and filters"""
    active_filters = filters.split('+')
    if 'stat_Read' in active_filters:
        query = " AND read_count > 0"
    elif 'stat_Unread' in active_filters:
        query = " AND read_count = 0"
    else:
        query = ""
    paras = {}
    for _filter in active_filters:
        if len(_filter) > 5:
            if _filter[0:5] == 'lang_':
                query += " AND language=:lang"
                paras['lang'] = _filter[5:]
            if  _filter[0:5] == 'form_':
                query += " AND form=:form"
                paras['form'] = _filter[5:]
    if shelf == 'Not shelfed':
        query += " AND shelf = ''"
    elif shelf != 'All':
        query += " AND shelf=:shelf"
        paras['shelf'] = shelf
    if query != '':
        query = " WHERE" + query[4:]
    return query, paras

def update(username, data):
    """Prepare updated or new data to be stored in the db"""
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
    else:
        data['reading_stats'] = []
        data['read_count'] = 0
    if book_id == 'new_book':
        book_id = insert_new_book(username, data)
    else:
        update_book(username, book_id, data)
    return book_id

def change_field(username, edit, old_name, new_name):
    """Updated a field for multiple books (used for mass edit)"""
    cursor, conn = db_sql.connect('books.db')
    if edit == 'series':
        sql = ("UPDATE " + username + " SET series = ? WHERE series = ?")
        cursor.execute(sql, (new_name, old_name, ))
    elif edit in VARIABLES.name_fields:
        sql = ("SELECT " + edit + ", _id FROM " + username + " WHERE " + edit +
               " LIKE ?")
        cursor.execute(sql, ('%"' + old_name + '"%', ))
        sql = ("UPDATE " + username + " SET " + edit + " = ? WHERE _id = ?")
        for book in cursor.fetchall():
            if len(book[edit]) == 1:
                cursor.execute(sql, ([new_name], book['_id'], ))
            else:
                field_new = []
                for name in book[edit]:
                    if name == old_name:
                        field_new.append(new_name)
                    else:
                        field_new.append(name)
                cursor.execute(sql, (field_new, book['_id'], ))
    conn.commit()
    conn.close()

def star_series(username, series_name, status):
    """Mark a series as compled"""
    cursor, conn = db_sql.connect('books.db')
    sql = ("UPDATE " + username + " SET series_complete = ? WHERE series = ?")
    if status == 'star':
        cursor.execute(sql, (0, series_name, ))
    else:
        cursor.execute(sql, (1, series_name, ))
    conn.commit()
    conn.close()

def get_by_id(username, book_id, field=None):
    """Get a book by its id and return its data"""
    cursor, conn = db_sql.connect('books.db')
    if field == None:
        sql = "SELECT * FROM " + username + " WHERE _id = ?"
        cursor.execute(sql, (book_id, ))
    else:
        sql = "SELECT " + field + " FROM " + username + " WHERE _id = ?"
        cursor.execute(sql, (book_id,))
    data = array_to_str(dict(cursor.fetchone()))
    conn.close()
    return data

def get_all(username):
    """Get all books and their data in the users db"""
    cursor, conn = db_sql.connect('books.db')
    cursor.execute("SELECT * FROM " + username)
    data = [array_to_str(dict(x)) for x in cursor.fetchall()]
    conn.close()
    return data

def aggregate_items(username, group_by, get_fields, shelf, _filter,
                    array=False):
    """Return a list of all books that statisfy the current filters"""
    cursor, conn = db_sql.connect('books.db')
    sql = ("SELECT " + group_by + ", " +
           ", ".join(get_fields) + " FROM " + username)
    query, paras = query_builder(_filter, shelf)
    cursor.execute(sql + query, paras)
    data = [dict(x) for x in cursor.fetchall()]
    data_temp = []
    if array:
        for row in data:
            if row[group_by] == None:
                row[group_by] = ['']
            temp_field = row[group_by][1:]
            row[group_by] = row[group_by][0]
            for value in temp_field:
                data_temp.append(copy(row))
                data_temp[-1][group_by] = value
        data += data_temp
    data = sorted(data, key=operator.itemgetter(group_by))
    list1 = []
    for key, items in itertools.groupby(data, operator.itemgetter(group_by)):
        list1.append({'_id': key, 'books': list(items)})
    conn.close()
    return list1

def series(username, shelf, variant, _filter):
    """Return a list of your books orderd by series"""
    order_by = variant.split('_')[1]
    if order_by == 'year':
        order_by = 'release_date AS order_nr'
    elif order_by == 'order':
        order_by = 'order_nr'
    data = aggregate_items(username, 'series',
                           ["title", "_id", order_by, "series_complete"],
                           shelf, _filter)
    data, data_temp = rearrange_data(data, 'Not in a series')
    if variant.split('_')[0] == 'variant1' and data_temp != None:
        for row in data_temp['books']:
            data.append({'_id' : row['title'],
                         'sub_items' : False,
                         'books' : {'_id' : row['_id']}})
        data = sorted_series(data, variant)
    else:
        data = sorted_series(data, variant)
        data = sort_append_rearranged(data_temp, data)
    return data

def author_and_more(username, sortby, shelf, variant, _filter):
    """Return a list of your books orderd by author or similar"""
    if sortby in VARIABLES.name_fields or sortby == 'genre':
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
    data, data_temp = rearrange_data(data, 'No ' + sortby)
    data = sorted_apg(data, sort_by_order, sortby)
    data = sort_append_rearranged(data_temp, data)
    return data

def titles(username, shelf, variant, _filter):
    """Return a list of your books orderd by title"""
    cursor, conn = db_sql.connect('books.db')
    sql = ("SELECT title, release_date, pages, _id FROM " + username)
    query, paras = query_builder(_filter, shelf)
    cursor.execute(sql + query, paras)
    data_temp = [dict(x) for x in cursor.fetchall()]
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
    conn.close()
    return sorted_titles(data, '_id', variant)

def covers(username, shelf, _filter):
    """Return a list of your book covers"""
    cursor, conn = db_sql.connect('books.db')
    sql = ("SELECT front, _id FROM " + username)
    query, paras = query_builder(_filter, shelf)
    cursor.execute(sql + query, paras)
    data_temp = [dict(x) for x in cursor.fetchall()]
    data = {}
    for row in data_temp:
        data[str(row["_id"])] = row["front"]
    conn.close()
    return data

def statistic_date(username, shelf, _filter, _type):
    """Date statistics"""
    _type = _type.split('#')
    cursor, conn = db_sql.connect('books.db')
    query, paras = query_builder(_filter, shelf)
    if _type[0] in ['release_date', 'add_date']:
        sql = ("SELECT " + _type[0] + " FROM " + username)
    else:
        sql = ("SELECT reading_stats FROM " + username)
    cursor.execute(sql + query, paras)
    data_temp = [dict(x) for x in cursor.fetchall()]
    data = []
    if len(_type) == 1:
        for row in data_temp:
            if _type[0] in ['release_date', 'add_date']:
                if row[_type[0]] != '':
                    data.append(row[_type[0]][0:4])
            else:
                for row2 in row["reading_stats"]:
                    if row2[_type[0]] != '':
                        data.append(row2[_type[0]][0:4])
    elif len(_type) == 2:
        for row in data_temp:
            if _type[0] in ['release_date', 'add_date']:
                if row[_type[0]] != '' and row[_type[0]][0:4] == _type[1]:
                    data.append(row[_type[0]][5:7])
            else:
                for row2 in row["reading_stats"]:
                    if (row2[_type[0]] != '' and
                            row2[_type[0]][0:4] == _type[1]):
                        data.append(row2[_type[0]][5:7])
    data = Counter(data)
    labels = sorted(list(data))
    data = [data[x] for x in labels]
    if labels != [] and labels[0] == "":
        labels[0] = "Unknown"
    conn.close()
    return labels, data

def statistic_pages_read(username, shelf, _filter, _type):
    """Pages read statistics"""
    _type = _type.split('#')
    cursor, conn = db_sql.connect('books.db')
    query, paras = query_builder(_filter, shelf)
    sql = ("SELECT reading_stats, pages FROM " + username)
    cursor.execute(sql + query, paras)
    data_temp = [dict(x) for x in cursor.fetchall()]
    data = []
    for row in data_temp:
        for row2 in row["reading_stats"]:
            if row2["finish_date"] != '' and row2["start_date"] != '':
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
    data = [data[x] for x in labels]
    labels = [str(x) for x in labels]
    conn.close()
    return labels, data

def statistic_pages_book(username, shelf, _filter):
    """Pages per book statistics"""
    cursor, conn = db_sql.connect('books.db')
    query, paras = query_builder(_filter, shelf)
    sql = ("SELECT pages FROM " + username)
    cursor.execute(sql + query, paras)
    data_temp = [dict(x) for x in cursor.fetchall()]
    data = []
    for row in data_temp:
        i = 0
        while len(row["pages"]) > i and row["pages"][i].isdigit():
            i = i+1
        if i > 0:
            data.append(round(int(row["pages"][0:i])/100-0.5)*100)
    data = Counter(data)
    labels = sorted(list(data))
    data = [data[x] for x in labels]
    labels = [str(x) + "-" + str(x+99) for x in labels]
    conn.close()
    return labels, data

def delete_by_id(username, book_id):
    """Delete a book by its id"""
    cursor, conn = db_sql.connect('books.db')
    sql = ("DELETE FROM " + username + " WHERE _id=?")
    cursor.execute(sql, (book_id, ))
    conn.commit()
    conn.close()

def shelf_list(username, _filter):
    """Return a list of all user shelfs"""
    query, paras = query_builder(_filter, 'All')
    sql = "SELECT DISTINCT shelf AS _id FROM " + username
    cursor, conn = db_sql.connect('books.db')
    cursor.execute(sql + query, paras)
    shelfs = [dict(x) for x in cursor.fetchall()]
    shelfs = sorted_shelfs(shelfs)
    shelfs.insert(0, {'_id' : 'All'})
    for shelf in shelfs:
        shelf['#items'] = count_items(username, shelf['_id'], _filter)
        if shelf['_id'] != '':
            shelf['name'] = shelf['_id']
        else:
            shelf['name'] = 'Not shelfed'
    conn.close()
    return shelfs

def autocomplete(username, query, field, array):
    """Return a list of suggestions"""
    cursor, conn = db_sql.connect('books.db')
    sql = ("SELECT DISTINCT " + field + " FROM " + username + " WHERE " +
           field + " LIKE ?")
    if array:
        cursor.execute(sql, ('%"' + query + '%', ))
        ac_list = []
        for book in cursor.fetchall():
            if len(book[field]) == 1:
                ac_list.append(book[field][0])
            else:
                for name in book[field]:
                    if name[0:len(query)] == query:
                        ac_list.append(name)
    else:
        cursor.execute(sql, (query + '%', ))
        ac_list = [x[field] for x in cursor.fetchall()]

    ac_list = [key for key, _ in itertools.groupby(sorted(ac_list))]
    conn.close()
    return {'suggestions' : ac_list}

def filter_list(username, shelf, field):
    """Return a list of all possible user filters"""
    cursor, conn = db_sql.connect('books.db')
    sql = "SELECT DISTINCT " + field + " AS '_id' FROM " + username
    if shelf == 'Not shelfed':
        shelf = ''
    if shelf != 'All':
        sql += " WHERE shelf = ?"
        cursor.execute(sql, (shelf, ))
    else:
        cursor.execute(sql)

    all_filters = [dict(x) for x in cursor.fetchall()]
    conn.close()
    return [x['_id'] for x in all_filters if x['_id'] != '']

def count_items(username, shelf, _filter):
    """Count books on a shelf"""
    cursor, conn = db_sql.connect('books.db')
    sql = "SELECT COUNT(*) AS items FROM " + username
    query, paras = query_builder(_filter, shelf)
    cursor.execute(sql + query, paras)
    items = cursor.fetchone()['items']
    conn.close()
    return str(items)

def drop(username):
    """Drop a users table"""
    cursor, conn = db_sql.connect('books.db')
    sql = 'DROP TABLE IF EXISTS ' + username
    cursor.execute(sql)
    conn.commit()
    conn.close()
