import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from hashlib import md5
from passlib.hash import pbkdf2_sha512
from datetime import date

from lib.sort_data import sorted_series, sorted_titles, sorted_shelfs
from lib.sort_data import sorted_authors
from lib.variables import name_fields

client = MongoClient('localhost', 9090)
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

def hash_remove_empty(data, warning):
    data_temp = None
    for row in data['result']:
        if row['_id'] == '':
            data_temp = row
            row['_id'] = warning
        row['item_hash'] = md5(row['item_hash'].encode('utf-8')).hexdigest()

    data = [x for x in data['result'] if x['_id'] != warning]
    return data, data_temp

def sort_insert_empty(data_temp, data):
    if data_temp != None:
            for book in data_temp['books']:
                del book['order']
            data_temp['books'] = sorted_titles(data_temp['books'], 'title')
            data.insert(0, data_temp)
    return data

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
                    temp[int(i)] = True
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

    def aggregate_items(self, group_by, get_fields, shelf, array=False):
        search = [{ "$group" : { "_id" : '$' + group_by,
                                "item_hash" : {"$last" : "$" + group_by},
                                "books" :{ "$push": get_fields}}}]
        if array:
            search.insert(0,{"$unwind" : "$" + group_by})
        if shelf != 'All':
            search.insert(0,{"$match" : {'shelf' : shelf}})
        data = self.collection.aggregate(search)
        return data

    def series(self, shelf, variant):
        data = self.aggregate_items('series',
                                    {"title": "$title", "_id": "$_id",
                                     "order": "$order",
                                     "series_complete": "$series_complete"},
                                    shelf)
        data, data_temp = hash_remove_empty(data, 'Not in a series')
        if variant == 1 and data_temp != None:
            for row in data_temp['books']:
                data.append({'_id' : row['title'],
                             'books' : {'_id' : row['_id']}})
            data = sorted_series(data)
        else:
            data = sorted_series(data)
            data = sort_insert_empty(data_temp, data)
        return data

    def authors(self, shelf):
        data = self.aggregate_items('authors', {"title": "$title",
                                                "_id": "$_id",
                                                "order": "$release_date"},
                                    shelf, True)
        data, data_temp = hash_remove_empty(data, 'No author')
        data = sorted_authors(data)
        data = sort_insert_empty(data_temp, data)
        return data

    def titles(self, shelf):
        if shelf == 'All':
            data_temp = self.collection.find({}, {"title" : 1} )
        else:
            data_temp = self.collection.find({"shelf" : shelf}, {"title" : 1} )
        data = []
        for row in data_temp:
            print(row)
            data.append({'_id' : row['title'],
                         'books' : {'_id' : row['_id']}})
            
        return sorted_titles(data)

    def ids(self):
        data = self.collection.find({},{'_id': 1})
        ids = []
        for row in data:
            ids.append( str(row['_id']) )
        return ids

    def delete_by_id(self, book_id):
        self.collection.remove({'_id' : ObjectId(book_id)})

    def shelfs(self):
        shelfs = self.collection.aggregate([{"$match" : {"shelf" :
                                                         {"$ne": ''} } },
                                            { "$group" : { "_id" : "$shelf"}}])
        shelfs = sorted_shelfs(shelfs['result'])
        shelfs.insert(0,{'_id' : 'All'})
        return shelfs

    def drop(self):
        self.collection.drop()

def mongo_add_user(username, password, session_id):
    user_info.insert({'username' : username,
                      'password' : pbkdf2_sha512.encrypt(password),
                      'session_id' : session_id,
                      'reg_date' : str(date.today()),
                      'role' : None})

def mongo_login(username, password, session_id):
    user = user_info.find_one({'username' : username})
    if user != None and pbkdf2_sha512.verify(password, user['password']):
        if session_id != None:
            user_info.update({'username' : username},
                             {"$set" : {"session_id" : session_id} })
        return True
    return False

def mongo_user(session_id):
    user = user_info.find_one({'session_id' : session_id})
    if user != None and 'role' not in user:
        user['role'] = None
    return user

def mongo_user_del(username):
    status = user_info.remove({"username" : username})
    return status

def mongo_role(username, role):
    status = user_info.update({"username" : username},
                              {"$set" : {"role" : role} })
    return status

def mongo_user_list():
    data = user_info.find({},{"_id" : 0}).sort([("username", 1)])
    return data
