from app.db.mongo import mongo_db
from shutil import rmtree
from os import remove

def del_all_books(mongo, username):
    mongo.drop()
    rmtree('static/covers/' + username + '_front/')
    return 0

def del_book(mongo, book_id):
    data = mongo.get_by_id(book_id)
    remove(data['front'])
    mongo.delete_by_id(book_id)
    return 0
