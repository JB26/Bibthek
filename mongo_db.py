import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from hashlib import md5

from sort_data import sorted_series

client = MongoClient('localhost', 9090)
db = client.bibthek
collection = db.jb_books

def mongo_insert(data):
    collection.insert(data)

def mongo_update(data):
    book_id = data['book_id']
    del data['book_id']
    if book_id == 'new_book':
        collection.insert(data)
    else:
        collection.update({'_id': ObjectId(book_id)}, {"$set" : data})

def mongo_get_by_id(book_id):
    return collection.find_one({'_id' : ObjectId(book_id)})

def mongo_series():
    data = collection.aggregate([{"$match" : {"series" : {"$ne": ''} } } , { "$group" : { "_id" : '$series', "series_hash" : {"$last" : "$series"}, "books" :{ "$push": {"title": "$title", "_id": "$_id", "order": "$order"}}}}])
    for row in data['result']:
        row['series_hash'] = md5(row['series_hash'].encode('utf-8')).hexdigest()
    data = data['result']
    data_temp = collection.find({"series":''}, {"title" : 1} )
    for row in data_temp:
        data.append({'_id' : row['title'], 'books' : {'_id' : row['_id']}}) #Append titles without a series
    return sorted_series(data)

def mongo_ids():
    data = collection.find({},{'_id': 1})
    ids = []
    for row in data:
        ids.append( str(row['_id']) )
    return ids

def mongo_delete_by_id(book_id):
    collection.remove({'_id' : ObjectId(book_id)})
