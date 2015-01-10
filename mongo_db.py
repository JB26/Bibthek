import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from hashlib import md5
from passlib.hash import pbkdf2_sha512

from sort_data import sorted_series
from variables import name_fields

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
        data['reading_stats'] = []
        if 'start_date' in data:
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
        if book_id == 'new_book':
            book_id = str(self.collection.insert(data))
        else:
            self.collection.update({'_id': ObjectId(book_id)}, {"$set" : data})
        return book_id

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

    def series(self, shelf):
        if shelf == 'All':
            data = self.collection.aggregate([{"$match" : {"series" : {"$ne": ''}} }, { "$group" : { "_id" : '$series', "series_hash" : {"$last" : "$series"}, "books" :{ "$push": {"title": "$title", "_id": "$_id", "order": "$order"}}}}])
        else:
            data = self.collection.aggregate([{"$match" : {"series" : {"$ne": ''}, 'shelf' : shelf} }, { "$group" : { "_id" : '$series', "series_hash" : {"$last" : "$series"}, "books" :{ "$push": {"title": "$title", "_id": "$_id", "order": "$order"}}}}])
        for row in data['result']:
            row['series_hash'] = md5(row['series_hash'].encode('utf-8')).hexdigest()
        data = data['result']
        if shelf == 'All':
            data_temp = self.collection.find({"series":''}, {"title" : 1} )
        else:
            data_temp = self.collection.find({"series":'', "shelf": shelf}, {"title" : 1} )
        for row in data_temp:
            data.append({'_id' : row['title'], 'books' : {'_id' : row['_id']}}) #Append titles without a series
        return sorted_series(data)

    def author(self, shelf):
        if shelf == 'All':
            data = self.collection.aggregate([{"$match" : {"author" : {"$ne": ''}} }, { "$group" : { "_id" : '$author', "author_hash" : {"$last" : "$author"}, "books" :{ "$push": {"title": "$title", "_id": "$_id", "order": "$order"}}}}])
        else:
            data = self.collection.aggregate([{"$match" : {"series" : {"$ne": ''}, 'shelf' : shelf} }, { "$group" : { "_id" : '$series', "series_hash" : {"$last" : "$series"}, "books" :{ "$push": {"title": "$title", "_id": "$_id", "order": "$order"}}}}])
        for row in data['result']:
            row['series_hash'] = md5(row['series_hash'].encode('utf-8')).hexdigest()
        data = data['result']
        if shelf == 'All':
            data_temp = self.collection.find({"series":''}, {"title" : 1} )
        else:
            data_temp = self.collection.find({"series":'', "shelf": shelf}, {"title" : 1} )
        for row in data_temp:
            data.append({'_id' : row['title'], 'books' : {'_id' : row['_id']}}) #Append titles without a series
        return sorted_series(data)

    def ids(self):
        data = self.collection.find({},{'_id': 1})
        ids = []
        for row in data:
            ids.append( str(row['_id']) )
        return ids

    def delete_by_id(self, book_id):
        self.collection.remove({'_id' : ObjectId(book_id)})

    def shelfs(self):
        shelfs = self.collection.aggregate([{"$match" : {"shelf" : {"$ne": '', "$ne": None} } } , { "$group" : { "_id" : "$shelf"}}])
        return shelfs['result']

def mongo_add_user(username, password, user_id):
    user_info.insert({'username' : username, 'password' : pbkdf2_sha512.encrypt(password), 'user_id' : user_id})

def mongo_login(username, password, user_id):
    user = user_info.find_one({'username' : username})
    if user != None and pbkdf2_sha512.verify(password, user['password']):
        user_info.update({'username' : username}, {"$set" : {"user_id" : user_id} })
        return True
    return False

def mongo_user(user_id):
    user = user_info.find_one({'user_id' : user_id})
    return user
