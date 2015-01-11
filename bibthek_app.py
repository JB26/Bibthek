from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
from cherrypy.lib import static
import json
from requests import get
from datetime import date
import hashlib
from random import random

import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

from mongo_db import mongo_db
from mongo_db import mongo_add_user, mongo_user, mongo_login
from variables import book_empty_default
from get_data import google_books_data
from import_sqlite3 import import_sqlite3
from export_csv import export_csv
from import_csv import import_csv
from export_cover import export_cover
import import_front
from sanity_check import sanity_check

mylookup = TemplateLookup(directories=['html'], output_encoding='utf-8',
                          encoding_errors='replace')

class bibthek(object):

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/books/All/series/variant1")

    @cherrypy.expose
    def books(self, shelf='All', sort_first=None, sort_second=None,
              book_id='new_book', book_type='book', json_data = False):
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
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
            new = True
        else:
            book = self.mongo.get_by_id(book_id)
            for k, v in book_empty.items():
                try:
                    book[k]
                except:
                    book[k] = v
            book['_id'] = str(book['_id'])
            new = False
        if json_data:
            return json.dumps(book)
        else:
            sort1 = [['Title', '/title', False],
                     ['Series', '/series/variant1', False],
                     ['Author', '/author/year', False]]
            if sort_first == 'title':
                items = self.mongo.titles(shelf)
                sort1[0][2] = True
                sort2 = [['Title', '/title', True]]
                active_sort = '/title'
            elif sort_first == 'series':
                sort1[1][2] = True
                sort2 = [['Variant 1', '/series/variant1', False],
                         ['Variant 2', '/series/variant2', False]]
                if sort_second == 'variant1':
                    items = self.mongo.series(shelf, 1)
                    sort2[0][2] = True
                    active_sort = '/series/variant1'
                if sort_second == 'variant2':
                    items = self.mongo.series(shelf, 2)
                    sort2[1][2] = True
                    active_sort = '/series/variant2'
            elif sort_first == 'author':
                sort1[2][2] = True
                sort2 = [['Year', '/series/year', False],
                         ['Title', '/series/title', False]]
                if sort_second == 'year':
                    items = self.mongo.authors(shelf)
                    sort2[0][2] = True
                    active_sort = '/series/year'
            mytemplate = mylookup.get_template("book.html")
            shelfs = self.mongo.shelfs()
            return mytemplate.render(items=items, book=book, new=new,
                                     shelfs=shelfs, active_shelf=shelf,
                                     sort1=sort1, sort2=sort2,
                                     active_sort=active_sort)

    @cherrypy.expose
    def menu(self, shelf='All'):
        mytemplate = mylookup.get_template("menu.html")
        series = self.mongo.series(shelf)
        shelfs = self.mongo.shelfs()
        return mytemplate.render(series=series, shelfs=shelfs)

    @cherrypy.expose
    def import_books(self, data_file=None, separator=None, cover_front=None):
        if data_file == None:
            mytemplate = mylookup.get_template("import.html")
            return mytemplate.render()
        elif data_file.file == None:
            mytemplate = mylookup.get_template("import.html")
            return mytemplate.render()
        else:
            data = data_file.file.read()
            username = cherrypy.session['username']
            new_name = username + '_' + data_file.filename
            with open('import/' + new_name , 'wb') as f:
                f.write(data)
            if data_file.filename.rsplit('.',1)[-1] == 'sqlite':
                data = import_sqlite3('import/' + new_name, separator)
            elif data_file.filename.rsplit('.',1)[-1] == 'csv':
                data = import_csv('import/' + new_name, separator)
            else:
                return "Only csv or sqlite"
            for row in data:
                self.mongo.insert(row)
            if cover_front.file != None:
                data = cover_front.file.read()
                new_name = username + '_front.tar'
                with open('import/' + new_name , 'wb') as f:
                    f.write(data)
                cover_list, error = import_front.untar(username)
                if error == 1: return 'Can not untar'
                for cover in cover_list:
                    book_id = self.mongo.get_by_cover(cover)
                    if book_id == None:
                        import_front.del_pic(cover, username)
                    else:
                        book_id = str(book_id['_id'])
                        new_name = import_front.move(cover, username, book_id)
                        self.mongo.update({'book_id' : book_id,
                                           'front' : new_name})
                import_front.del_dir(username)
            return 'Upload complete'

    @cherrypy.expose
    def export(self):
        data = self.mongo.get_all()
        file_name = export_csv(data, cherrypy.session['username'])
        path = os.path.join(absDir, file_name)
        return static.serve_file(path, "application/x-download",
                                 "attachment", os.path.basename(path))

    @cherrypy.expose
    def export_covers(self):
        data = self.mongo.get_all()
        file_name = export_cover(data, cherrypy.session['username'])
        path = os.path.join(absDir, file_name)
        return static.serve_file(path, "application/x-download",
                                 "attachment", os.path.basename(path))
        
    @cherrypy.expose
    def save(self, **params):
        params = sanity_check(params)
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
        if params['title'] == '':
            return 'Please enter a title!'
        if params['book_id'] == 'new_book':
            new = True
        else:
            new = False
        if params['front'].file != None:
            file_type =  params['front'].filename.rsplit('.',1)[-1]
            if file_type not in  ['jpg', 'png', 'jpeg']:
                return "Only png and jpg", 1
            new_name = hashlib.sha224( bytes( str(random()) + params['book_id'],
                                      'utf-8')).hexdigest()
            new_name = "front/" + new_name + '.' + file_type
            with open('html/' + new_name, 'wb') as f:
                    f.write(params['front'].file.read())
            params['front'] = new_name
            if new == False:
                data = self.mongo.get_by_id(params['book_id'])
                try:
                    os.remove('html/' + data['front'])
                except:
                    pass 
        else:
            del params['front']
        print(params)
        book_id = self.mongo.update(params)
        return json.dumps({'book_id' : book_id, 'new' : new})

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
            gr_id = get('https://www.goodreads.com/book/isbn_to_id/' +
                        book['isbn']  + '?key=Fyl3BYyRgNUZAoD1M9rQ').text
        elif isbn != '':
            gr_id = get('https://www.goodreads.com/book/isbn_to_id/' +
                        isbn  + '?key=Fyl3BYyRgNUZAoD1M9rQ').text
        raise cherrypy.HTTPRedirect("https://www.goodreads.com/book/show/" +
                                    gr_id)

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
    def sort(self, sort):
        cherrypy.session['sort'] = sort

    @cherrypy.expose
    def login(self, username = '', password = ''):
        if username == '' and password == '':
            mytemplate = mylookup.get_template("login.html")
            return mytemplate.render()
        elif mongo_login(username, password, cherrypy.session.id):
            #Make sure the session ID stops changing
            cherrypy.session['username'] = username
            self.mongo = mongo_db(username)
            raise cherrypy.HTTPRedirect("/")
        else:
            return "Login problem"

if __name__ == '__main__':
    cherrypy.quickstart(bibthek(), '/', 'app.conf')
