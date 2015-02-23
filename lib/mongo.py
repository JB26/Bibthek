from pymongo import MongoClient
from bson.objectid import ObjectId
from passlib.hash import pbkdf2_sha512
from datetime import date
import configparser
import re
import random
import string
from collections import Counter

from lib.sort_data import sorted_series, sorted_titles, sorted_shelfs
from lib.sort_data import sorted_apg
from lib.variables import name_fields

config = configparser.ConfigParser()
config.read('db.conf')

client = MongoClient( config['Database']['host'],
                      int(config['Database']['port']))

user_info = client.bibthek_users.info

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
    for row in data['result']:
        if row['_id'] == '':
            data_temp = row
            row['_id'] = warning
            row['empty_field'] = True
        else:
            row['empty_field'] = False
        row['sub_items'] = True

    data = [x for x in data['result'] if x['_id'] != warning]
    return data, data_temp

def sort_insert_empty(data_temp, data):
    if data_temp != None:
            data_temp['books'] = sorted_titles(data_temp['books'], 'title')
            data.append(data_temp)
    return data

def query_filter(filters):
    filter_list = filters.split('+')
    if 'stat_Read' in filter_list:
        query = {'reading_stats.0' : { "$exists" : True}}
    elif 'stat_Unread' in filter_list:
        query = {'reading_stats.0' : { "$exists" : False}}
    else:
        query = {}
    if 'form_Physical' in filter_list:
        query['form'] = { '$in' : [None, 'Physical']}
    elif 'form_Digital' in filter_list:
        query['form'] = 'Digital'
    elif 'form_Borrowed' in filter_list:
        query['form'] = 'Borrowed'
    for _filter in filter_list:
        if len(_filter) > 5:
            if _filter[0:5] == 'lang_':
                query['language'] = _filter[5:]
            if  _filter[0:5] == 'bind_':
                query['binding'] = _filter[5:]
    return query

class mongo_db:
    def __init__(self, username):
        self.collection = client.bibthek[username]

    def insert(self, data):
        data = str_to_array(data)
        book_id = str(self.collection.insert(data))
        return book_id

    def update(self, data):
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
            book_id = str(self.collection.insert(data))
        else:
            self.collection.update({'_id': ObjectId(book_id)}, {"$set" : data})
        return book_id

    def change_field(self, edit, old_name, new_name):
        if edit == 'series':
            self.collection.update({edit : old_name},
                                   {"$set" : {edit : new_name}}, multi=True)
        elif edit in name_fields:
            self.collection.update({edit : old_name},
                                   {"$set" : {edit + ".$" : new_name}},
                                   multi=True)

    def star_series(self, series, status):
        if status == 'star':
            data = {'series_complete' : False}
        else:
            data = {'series_complete' : True}
        self.collection.update({'series': series}, {"$set" : data})

    def get_by_id(self, book_id, field = None):
        if field == None:
            data = self.collection.find_one({'_id' : ObjectId(book_id)})
        else:
            data = self.collection.find_one({'_id' : ObjectId(book_id)},
                                            {field : 1, '_id' : 0})
        data = array_to_str(data)
        return data

    def get_by_cover(self, cover):
        return self.collection.find_one({'front' : cover}, {'_id':1})

    def get_all(self):
        data = []
        for row in self.collection.find({}, {'_id':0}):
            row = array_to_str(row)
            data.append(row)
        return data

    def aggregate_items(self, group_by, get_fields, shelf, _filter,
                        array=False):
        search = [{ "$group" : { "_id" : '$' + group_by,
                                "books" :{ "$push": get_fields}}}]
        if array:
            search.insert(0,{"$unwind" : "$" + group_by})
        query = query_filter(_filter)
        if shelf == 'Not shelfed':
            query['shelf'] = ''
        elif shelf != 'All':
            query['shelf'] = shelf
        search.insert(0,{"$match" : query})
        data = self.collection.aggregate(search)
        return data
    
    def series(self, shelf, variant, _filter):
        order_by = variant.split('_')[1]
        if order_by == 'year':
            order_by = 'release_date'
        data = self.aggregate_items('series',
                                    {"title": "$title", "_id": "$_id",
                                     "order": "$" + order_by,
                                     "series_complete": "$series_complete"},
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

    def author_and_more(self, sortby, shelf, variant, _filter):
        if sortby in name_fields or sortby == 'genre':
            array = True
        else:
            array = False
        if variant == 'year':
            data = self.aggregate_items(
                sortby,
                {
                    "title": "$title", "_id": "$_id",
                    "order": "$release_date"
                },
                shelf, _filter, array
                )
            sort_by_order = True
        elif variant == 'title':
            data = self.aggregate_items(
                sortby, {"title": "$title", "_id": "$_id"}, shelf,
                _filter, array
                )
            sort_by_order = False
        data, data_temp = remove_empty_field(data, 'No ' + sortby)
        data = sorted_apg(data, sort_by_order, sortby)
        data = sort_insert_empty(data_temp, data)
        return data

    def titles(self, shelf, variant, _filter):
        query = query_filter(_filter)
        if shelf == 'Not shelfed':
            query['shelf'] = ''
        elif shelf != 'All':
            query['shelf'] = shelf
        if variant == 'title':
            data_temp = self.collection.find(query, {"title" : 1})
        elif variant == 'year':
            data_temp = self.collection.find(query, {"title" : 1,
                                                     "release_date" : 1} )
        elif variant == 'pages':
             data_temp = self.collection.find(query, {"title" : 1,
                                                      "pages" : 1} )
        data = []
        for row in data_temp:
            temp = {'_id' : row['title'],
                    'sub_items' : False,
                    'books' : {'_id' : row['_id']}}
            if variant == 'year':
                temp['order'] = row['release_date']
            elif variant == 'pages':
                temp['order'] = row['pages']
            data.append(temp)
        return sorted_titles(data, '_id', variant)

    def covers(self, shelf, _filter):
        query = query_filter(_filter)
        if shelf == 'Not shelfed':
            query['shelf'] = ''
        elif shelf != 'All':
            query['shelf'] = shelf
        data_temp = self.collection.find(query, {"front" : 1})
        data = {}
        for row in data_temp:
            data[str(row["_id"])] = row["front"]
        return data

    def ids(self):
        data = self.collection.find({},{'_id': 1})
        ids = []
        for row in data:
            ids.append( str(row['_id']) )
        return ids

    def statistic_date_easy(self, shelf, _filter, _type):
        _type = _type.split('#')
        query = query_filter(_filter)
        if shelf == 'Not shelfed':
            query['shelf'] = ''
        elif shelf != 'All':
            query['shelf'] = shelf
        data_temp = self.collection.find(query, {"_id" : 0, _type[0] : 1} )
        data = []
        if len(_type) == 1:
            for row in data_temp:
                if row[_type[0]]  != '':
                    data.append(row[_type[0]][0:4])
        elif len(_type) == 2:
            for row in data_temp:
                if row[_type[0]]  != '' and row[_type[0]][0:4] == _type[1]:
                    data.append(row[_type[0]][5:7])
        data = Counter(data)
        labels = sorted(list(data))
        data = [ data[x] for x in labels  ]
        if labels[0] == "":
            labels[0] = "Unknown"
        return labels, data

    def statistic_date_hard(self, shelf, _filter, _type):
        _type = _type.split('#')
        query = query_filter(_filter)
        if shelf == 'Not shelfed':
            query['shelf'] = ''
        elif shelf != 'All':
            query['shelf'] = shelf
        data_temp = self.collection.find(query, {"_id" : 0,
                                                 "reading_stats" : 1} )
        data = []
        if len(_type) == 1:
            for row in data_temp:
                for row2 in row["reading_stats"]:
                    if row2[_type[0]]  != '':
                        data.append(row2[_type[0]][0:4])
        elif len(_type) == 2:
            for row in data_temp:
                for row2 in row["reading_stats"]:
                    if (row2[_type[0]]  != '' and
                        row2[_type[0]][0:4] == _type[1]):
                        data.append(row2[_type[0]][5:7])
        data = Counter(data)
        labels = sorted(list(data))
        data = [ data[x] for x in labels  ]
        if labels[0] == "":
            labels[0] = "Unknown"
        return labels, data

    def statistic_pages_read(self, shelf, _filter, _type):
        _type = _type.split('#')
        query = query_filter(_filter)
        if shelf == 'Not shelfed':
            query['shelf'] = ''
        elif shelf != 'All':
            query['shelf'] = shelf
        data_temp = self.collection.find(query, {"_id" : 0,
                                                 "reading_stats" : 1,
                                                 "pages" : 1} )
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

    def statistic_pages_book(self, shelf, _filter):
        query = query_filter(_filter)
        if shelf == 'Not shelfed':
            query['shelf'] = ''
        elif shelf != 'All':
            query['shelf'] = shelf
        data_temp = self.collection.find(query, {"_id" : 0,
                                                 "pages" : 1} )
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

    def delete_by_id(self, book_id):
        self.collection.remove({'_id' : ObjectId(book_id)})

    def shelfs(self, _filter):
        shelfs = self.collection.aggregate([{ "$group" : { "_id" : "$shelf"}}])
        shelfs = sorted_shelfs(shelfs['result'])
        shelfs.insert(0,{'_id' : 'All'})
        for shelf in shelfs:
            shelf['#items'] = self.count_items(shelf['_id'], _filter)
            if shelf['_id'] != '':
                shelf['name'] = shelf['_id']
            else:
                shelf['name'] = 'Not shelfed'
        return shelfs

    def autocomplete(self, query, field, array):
        search = [{"$match" : {field : {"$regex": query} } },
                 { "$group" : {"_id" : "$" + field}}]
        if array:
            search.insert(0,{"$unwind" : "$" + field})
        ac_list = self.collection.aggregate(search)
        ac_list = {'suggestions' : [ x['_id'] for x in ac_list['result'] ]}
        return ac_list

    def filter_list(self, shelf, field):
        search = [{ "$group" : {"_id" : "$" + field}}]
        if shelf == 'Not shelfed':
            shelf = ''
        if shelf != 'All':
            search.insert(0,{ "$match" : {"shelf" : shelf}})
        filter_list = self.collection.aggregate(search)
        return [ x['_id'] for x in filter_list['result'] if x['_id'] != '']

    def count_items(self, shelf, _filter):
        query = query_filter(_filter)
        if shelf == 'Not shelfed':
            query['shelf'] = ''
        elif shelf != 'All':
            query['shelf'] = shelf
        items = self.collection.find(query).count()
        return str(items)

def mongo_add_user(username, password, email, session_id):
    p = re.compile('[A-Z-+_0-9]+', re.IGNORECASE)
    m = p.match(username)
    if m == None:
        return '"' + username[0] + '" not allowed in the username'
    elif m.group() != username:
        return '"' + username[m.span()[1]] + '" not allowed in the username'
    if user_info.find_one({'username' : username}) != None:
        return "Username already exists"
    query = {'username' : username,
             'password' : pbkdf2_sha512.encrypt(password),
             'session_id' : session_id,
             'reg_date' : str(date.today()),
             'role' : None}
    if email != '' :
        query['email'] = email
    user_info.insert(query)
    return '0'

def mongo_login(username, password, session_id):
    user = user_info.find_one({'username' : username})
    if user != None and pbkdf2_sha512.verify(password, user['password']):
        sessions = user_info.find_one({"username" : username},
                                      {"session_id" : 1})
        sessions = sessions['session_id']
        try:
            sessions.append(session_id)
        except AttributeError:
            sessions = [session_id]
        user_info.update({'username' : username},
                         {"$set" : {"session_id" : sessions} })
        return True
    return False

def mongo_logout(session_id, username):
    sessions = user_info.find_one({'session_id' : session_id})['session_id']
    sessions.remove(session_id)
    user_info.update({'username' : username},
                         {"$set" : {"session_id" : sessions} })

def mongo_logout_all(username):
    user_info.update({'username' : username},
                         {"$set" : {"session_id" : None} })    

def mongo_user(username):
    user = user_info.find_one({'username' : username})
    if user != None and 'role' not in user:
        user['role'] = None
    return user

def mongo_user_by_session(session_id):
    return user_info.find_one({'session_id' : session_id})
        

def mongo_change_pw(username, password_old, password_new):
    user = user_info.find_one({'username' : username})
    if pbkdf2_sha512.verify(password_old, user['password']):
        user_info.update({'username' : username},
                         {"$set" : {"password" :
                                    pbkdf2_sha512.encrypt(password_new)} })
        return "0"
    else:
        return "Wrong password"

def mongo_reset_pw(username):
    password_new = ''.join(random.SystemRandom().
                           choice(string.ascii_uppercase + string.digits)
                           for _ in range(6))
    user_info.update({'username' : username},
                         {"$set" : {"password" :
                                    pbkdf2_sha512.encrypt(password_new)} })
    return password_new

def mongo_change_email(username, email):
     user_info.update({'username' : username}, {"$set" : {"email" : email } } )

def mongo_user_del(username):
    status = user_info.remove({"username" : username})
    return status

def mongo_role(username, role):
    status = user_info.update({"username" : username},
                              {"$set" : {"role" : role} })
    return status

def mongo_privacy(username, status):
    user_info.update({'username' : username},
                     {"$set" : {"privacy" : status } } )
    
def mongo_user_list():
    data = user_info.find({},{"_id" : 0}).sort([("username", 1)])
    return data

def mongo_drop(username):
    client.bibthek[username].drop()
