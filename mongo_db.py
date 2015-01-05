import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from hashlib import md5
from passlib.hash import pbkdf2_sha512

from sort_data import sorted_series

client = MongoClient('localhost', 9090)
user_info = client.bibthek_users.info

class mongo_db:
    def __init__(self, username):
        self.collection = client.bibthek[username]

    def insert(self, data):
        self.collection.insert(data)

    def update(self, data):
        book_id = data['book_id']
        del data['book_id']
        if book_id == 'new_book':
            self.collection.insert(data)
        else:
            self.collection.update({'_id': ObjectId(book_id)}, {"$set" : data})

    def get_by_id(self, book_id):
        return self.collection.find_one({'_id' : ObjectId(book_id)})

    def get_all(self):
        data = []
        for row in self.collection.find({}, {'_id':0}):
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
