"""Delete books and their covers"""
from shutil import rmtree
from os import remove

import lib.db_sql as db_sql
import lib.db_books as db_books

def del_all_books(username):
    """Delete all books from a user"""
    db_books.drop(username)
    db_sql.init_books(username)
    try:
        rmtree('static/covers/' + username + '_front/')
    except FileNotFoundError:
        print("No cover to delete")
    return 0

def del_book(username, book_id):
    """Delete a single books from a user"""
    data = db_books.get_by_id(username, book_id)
    if data['front'] != None:
        try:
            remove(data['front'])
        except FileNotFoundError:
            print("No cover to delete")
    db_books.delete_by_id(username, book_id)
    return 0
