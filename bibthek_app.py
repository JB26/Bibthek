from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
import json
from requests import get

import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

from mongo_db import mongo_db
from mongo_db import mongo_add_user, mongo_user, mongo_login
from variables import fieldnames
from get_data import google_books_data
from import_sqlite3 import import_sqlite3

mylookup = TemplateLookup(directories=['html'], output_encoding='utf-8', encoding_errors='replace')

class bibthek(object):

    def book_empty_default(self):
        book_empty = {name : '' for name in fieldnames}
        book_empty['front'] =  'icons/circle-x.svg'
        book_empty['_id'] = 'new_book'
        book_empty['type'] = 'book'
        return book_empty

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/book")

    @cherrypy.expose
    def book(self, shelf='All', book_id='new_book', book_type='book', json_data = False):
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
        book_empty = self.book_empty_default()
        if book_id=='new_book':
            book = book_empty
            if book_type == 'comic':
                book['type'] = 'comic'
            else:
                book['type'] = 'book'
            if shelf != 'All':
                book['shelf'] = shelf
            new = True
        else:
            book = self.mongo.get_by_id(book_id)
            for k, v in book_empty.items():
                try:
                    book[k]
                except:
                    book[k] = v
                    print(k + "=" + v)
            if isinstance(book[k], list):
                book[k] = ' & '.join(book[k])
            book['_id'] = str(book['_id'])
            new = False
        print(book['type'])
        if json_data:
            return json.dumps(book)
        else:
            mytemplate = mylookup.get_template("book.html")
            series = self.mongo.series(shelf)
            shelfs = self.mongo.shelfs()
            return mytemplate.render(series=series, book=book, new=new, shelfs=shelfs, selected=shelf)

    @cherrypy.expose
    def menu(self, shelf='All'):
        mytemplate = mylookup.get_template("menu.html")
        series = self.mongo.series(shelf)
        shelfs = self.mongo.shelfs()
        return mytemplate.render(series=series, shelfs=shelfs)

    @cherrypy.expose
    def import_books(self, data_file=None):
        if data_file == None:
            mytemplate = mylookup.get_template("import.html")
            return mytemplate.render()
        else:
            data = data_file.file.read()
            new_name =  cherrypy.session.id + '_' + data_file.filename
            with open('import/' + new_name , 'wb') as f:
                f.write(data)
            data = import_sqlite3('import/' + new_name)
            for row in data:
                self.mongo.insert(row)
            return 'Upload complete'

    @cherrypy.expose
    def export(self):
        return test
        

    @cherrypy.expose
    def save(self, **params):
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
        self.mongo.update(params)

    @cherrypy.expose
    def new_isbn(self, isbn):
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
        book = google_books_data(isbn)
        return json.dumps(book)

    @cherrypy.expose
    def gr_id(self, book_id='', isbn=''):
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
        if book_id != '':
            book = self.mongo.get_by_id(book_id)
            gr_id = get('https://www.goodreads.com/book/isbn_to_id/' + book['isbn']  + '?key=Fyl3BYyRgNUZAoD1M9rQ').text
        elif isbn != '':
            gr_id = get('https://www.goodreads.com/book/isbn_to_id/' + isbn  + '?key=Fyl3BYyRgNUZAoD1M9rQ').text
        raise cherrypy.HTTPRedirect("https://www.goodreads.com/book/show/" + gr_id)

    @cherrypy.expose
    def delete(self, book_id):
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
        self.mongo.delete_by_id(book_id)
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def register(self, secret = '', username = '', password = '', mail = ''):
        if password and username is not '':
            mongo_add_user(username, password, cherrypy.session.id)
        else:
            mytemplate = mylookup.get_template("register.html")
            return mytemplate.render()

    @cherrypy.expose
    def shelf(self, shelf):
        if shelf=='All':
            raise cherrypy.HTTPRedirect("/book")
        else:
           raise cherrypy.HTTPRedirect("/book/" + shelf) 

    @cherrypy.expose
    def login(self, username = '', password = ''):
        if username == '' and password == '':
            mytemplate = mylookup.get_template("login.html")
            return mytemplate.render()
        elif mongo_login(username, password, cherrypy.session.id):
            cherrypy.session['LogedIn'] = True #Make sure the session ID stops changing
            self.mongo = mongo_db(username)
            raise cherrypy.HTTPRedirect("/")
        else:
            return "Login problem"

if __name__ == '__main__':
    cherrypy.quickstart(bibthek(), '/', 'app.conf')
