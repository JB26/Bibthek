from datetime import date
from lib.mongo import mongo_db
from lib.variables import book_empty_default

def book_data(mongo, book_id, book_type, shelf):
    book_empty = book_empty_default()
    if book_id=='new_book':
        book = book_empty
        book['add_date'] = str(date.today())
        if book_type == 'comic':
            book['type'] = 'comic'
        else:
            book['type'] = 'book'
        if shelf != 'All':
            book['shelf'] = shelf
    else:
        book = mongo.get_by_id(book_id)
        for k, v in book_empty.items():
            try:
                book[k]
            except:
                book[k] = v
        book['_id'] = str(book['_id'])
    return book
