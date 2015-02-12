from lib.mongo import mongo_drop
from shutil import rmtree
from os import remove

def del_all_books(username):
    mongo_drop(username)
    try:
        rmtree('static/covers/' + username + '_front/')
    except FileNotFoundError:
        print("No cover to delete")
    return 0

def del_book(mongo, book_id):
    data = mongo.get_by_id(book_id)
    if 'front' in data:
        remove(data['front'])
    mongo.delete_by_id(book_id)
    return 0
