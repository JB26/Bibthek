from datetime import date
from lib.mongo import mongo_db
from lib.variables import book_empty_default
from lib.sanity_check import sanity_check
import os
import hashlib
import cherrypy
from random import random

def get_book_data(mongo, book_id, book_type, shelf):
    book_empty = book_empty_default()
    if book_id in ['new_book', 'new_comic']:
        book = book_empty
        book['add_date'] = str(date.today())
        if book_id == 'new_comic':
            book['type'] = 'comic'
        else:
            book['type'] = 'book'
        if shelf != 'All':
            book['shelf'] = shelf
    else:
        book = mongo.get_by_id(book_id)
        for k, v in book_empty.items():
            if k not in book:
                book[k] = v
        book['_id'] = str(book['_id'])
    return book

def save_book_data(mongo, params):
    params, error = sanity_check(params)
    if error != "0":
        return None, None, error
    if params['book_id'] == 'new_book':
        new = True
    else:
        new = False
    if params['front'].file != None:
        file_type =  params['front'].filename.rsplit('.',1)[-1]
        if file_type not in  ['jpg', 'png', 'jpeg']:
            return None, None, "Only png and jpg"
        new_name, error = cover_name(cherrypy.session['username'], file_type)
        if error != '0':
            return  None, None, error
        try:
            os.mkdir(new_name.rsplit('/')[0])
        except FileExistsError:
            pass
        with open(new_name, 'wb') as f:
                f.write(params['front'].file.read())
        params['front'] = new_name
        if new == False:
            data = mongo.get_by_id(params['book_id'])
            try:
                os.remove(data['front'])
            except FileNotFoundError:
                pass 
    else:
        del params['front']
    book_id = mongo.update(params)
    return book_id, new, "0"

def cover_name(username, file_type):
    first_run = True
    i = 0
    path =  "static/covers/" + username + '_front/'
    while first_run or (os.path.isfile(new_name) and i < 5):
        first_run = False
        new_name = hashlib.sha224( bytes( str(random()),
                                          'utf-8')).hexdigest()
        new_name = path  + new_name + '.' + file_type
        i = i+1
    if i == 5:
        return None, "Wtf? Couldn't generate new cover name! Try again?"
    else:
        return new_name, '0'
