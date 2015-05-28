from shutil import rmtree
from os import remove

import lib.db_sql as db_sql

def del_all_books(username):
    db_sql.drop(username)
    db_sql.init_books(username)
    try:
        rmtree('static/covers/' + username + '_front/')
    except FileNotFoundError:
        print("No cover to delete")
    return 0

def del_book(username, book_id):
    data = db_sql.get_by_id(username, book_id)
    if data['front'] != None:
        try:
            remove(data['front'])
        except FileNotFoundError:
            print("No cover to delete")
    db_sql.delete_by_id(username, book_id)
    return 0
