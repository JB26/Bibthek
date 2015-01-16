from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
from cherrypy.lib import static
import json
from requests import get
from datetime import date
import hashlib
from random import random
import argparse

import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

from lib.mongo import mongo_db, mongo_user_list, mongo_user_del
from lib.mongo import mongo_add_user, mongo_user, mongo_login, mongo_role
from lib.variables import book_empty_default
from lib.get_data import google_books_data
from lib.import_data import import_file
from lib.export_data import export_csv, export_cover_csv
from lib.sanity_check import sanity_check
from lib.del_books import del_all_books, del_book
import lib.auth as auth

mylookup = TemplateLookup(directories=['html'], output_encoding='utf-8',
                          encoding_errors='replace')

class bibthek(object):

    def db(self):
        return mongo_db(cherrypy.session['username'])

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/books/All/series/variant1")

    @cherrypy.expose
    def books(self, shelf='All', sort_first=None, sort_second=None,
              book_id='new_book', book_type='book', json_data = False):
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
            book = self.db().get_by_id(book_id)
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
                items = self.db().titles(shelf)
                sort1[0][2] = True
                sort2 = [['Title', '/title', True]]
                active_sort = '/title'
            elif sort_first == 'series':
                sort1[1][2] = True
                sort2 = [['Variant 1', '/series/variant1', False],
                         ['Variant 2', '/series/variant2', False]]
                if sort_second == 'variant1':
                    items = self.db().series(shelf, 1)
                    sort2[0][2] = True
                    active_sort = '/series/variant1'
                if sort_second == 'variant2':
                    items = self.db().series(shelf, 2)
                    sort2[1][2] = True
                    active_sort = '/series/variant2'
            elif sort_first == 'author':
                sort1[2][2] = True
                sort2 = [['Year', '/author/year', False],
                         ['Title', '/author/title', False]]
                if sort_second == 'year':
                    items = self.db().authors(shelf)
                    sort2[0][2] = True
                    active_sort = '/author/year'
            mytemplate = mylookup.get_template("book.html")
            shelfs = self.db().shelfs()
            return mytemplate.render(items=items, book=book, new=new,
                                     shelfs=shelfs, active_shelf=shelf,
                                     sort1=sort1, sort2=sort2,
                                     active_sort=active_sort)

    @cherrypy.expose
    def menu(self, shelf='All'):
        mytemplate = mylookup.get_template("menu.html")
        series = self.db().series(shelf)
        shelfs = self.db().shelfs()
        return mytemplate.render(series=series, shelfs=shelfs)

    @cherrypy.expose
    def settings(self):
        user = mongo_user(cherrypy.session.id)
        user_role = user['role']
        mytemplate = mylookup.get_template("user.html")
        return mytemplate.render(user_role=user_role)


    @cherrypy.expose
    @cherrypy.tools.auth(user_role='admin')
    def admin(self):
        user_list = mongo_user_list()
        mytemplate = mylookup.get_template("admin.html")
        return mytemplate.render(user_role='admin', user_list=user_list)

    @cherrypy.expose
    def delete_acc(self, password):
        if mongo_login(cherrypy.session['username'], password, None):
            del_all_books(self.db(), cherrypy.session['username'])
            mongo_user_del(cherrypy.session['username'])
            cherrypy.lib.sessions.expire()
            raise cherrypy.HTTPRedirect("/")
        else:
            print('Nope!')
        

    @cherrypy.expose
    def import_books(self, data_upload=None, separator=None):
        if data_upload == None or data_upload.file == None:
            user = mongo_user(cherrypy.session.id)
            user_role = user['role']
            mytemplate = mylookup.get_template("import.html")
            return mytemplate.render(user_role=user_role)
        else:
            data = data_upload
            username = cherrypy.session['username']
            data, error = import_file(data, username, separator)
            if error != '0':
                return error
            else:
                for row in data:
                    self.db().insert(row)           
                return 'Upload complete'

    @cherrypy.expose
    def export(self, _type):
        data = self.db().get_all()
        if _type == 'csv':
            file_name = export_csv(data, cherrypy.session['username'])
        elif _type == 'cover_csv':
            file_name = export_cover_csv(data, cherrypy.session['username'])
        path = os.path.join(absDir, file_name)
        return static.serve_file(path, "application/x-download",
                                 "attachment", os.path.basename(path))
        
    @cherrypy.expose
    def save(self, **params):
        params = sanity_check(params)
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
            path =  "static/covers/" + cherrypy.session['username'] + '_front/'
            try:
                os.mkdir(path)
            except:
                pass
            new_name = path  + new_name + '.' + file_type
            with open(new_name, 'wb') as f:
                    f.write(params['front'].file.read())
            params['front'] = new_name
            if new == False:
                data = self.db().get_by_id(params['book_id'])
                try:
                    os.remove(data['front'])
                except:
                    pass 
        else:
            del params['front']
        book_id = self.db().update(params)
        return json.dumps({'book_id' : book_id, 'new' : new})

    @cherrypy.expose
    def batch_edit(self, edit, old_name, new_name):
        if edit in  ['series', 'authors']:
            self.db().change_field(edit, old_name, new_name)
            raise cherrypy.HTTPRedirect( str(cherrypy.request.headers
                                            .elements('Referer')[0]) )

    @cherrypy.expose
    def star_series(self, series, status):
        self.db().star_series(series, status)
        return '0'

    @cherrypy.expose
    def new_isbn(self, isbn):
        book = google_books_data(isbn)
        return json.dumps(book)

    @cherrypy.expose
    def gr_id(self, book_id='', isbn=''):
        if book_id != '':
            book = self.db().get_by_id(book_id)
            gr_id = get('https://www.goodreads.com/book/isbn_to_id/' +
                        book['isbn']  + '?key=Fyl3BYyRgNUZAoD1M9rQ').text
        elif isbn != '':
            gr_id = get('https://www.goodreads.com/book/isbn_to_id/' +
                        isbn  + '?key=Fyl3BYyRgNUZAoD1M9rQ').text
        raise cherrypy.HTTPRedirect("https://www.goodreads.com/book/show/" +
                                    gr_id)

    @cherrypy.expose
    def delete(self, book_id):
        del_book(self.db(), book_id)
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def delete_all(self):
        del_all_books(self.db(), cherrypy.session['username'])

    @cherrypy.expose
    def logout(self):
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    @cherrypy.tools.auth(required = False)
    def register(self, secret = '', username = '', password = '', mail = ''):
        if password and username is not '':
            mongo_add_user(username, password, cherrypy.session.id)
        else:
            mytemplate = mylookup.get_template("register.html")
            return mytemplate.render()

    @cherrypy.expose
    @cherrypy.tools.auth(required = False)
    def login(self, username = '', password = ''):
        if username == '' and password == '':
            mytemplate = mylookup.get_template("login.html")
            return mytemplate.render()
        elif mongo_login(username, password, cherrypy.session.id):
            #Make sure the session ID stops changing
            cherrypy.session['username'] = username
            raise cherrypy.HTTPRedirect("/")
        else:
            return "Login problem"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BibThek')
    parser.add_argument('--admin', type = str,
                        help = 'The user you want to make an admin',
                        metavar = "Username")
    args = parser.parse_args()
    if args.admin != None:
        print(mongo_admin(args.admin, 'admin'))
    cherrypy.quickstart(bibthek(), '/', 'app.conf')
