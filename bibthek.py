from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
from cherrypy.lib import static
import json
from requests import get

import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

from lib.mongo import mongo_db, mongo_user_list, mongo_user_del, mongo_change_pw
from lib.mongo import mongo_add_user, mongo_user, mongo_login, mongo_role
from lib.mongo import mongo_change_email, mongo_reset_pw
from lib.book_data import get_book_data, save_book_data
from lib.get_data import google_books_data
from lib.import_data import import_file
from lib.export_data import export_csv, export_cover_csv
from lib.del_books import del_all_books, del_book
import lib.auth as auth
from lib.menu_data import menu_data, menu_filter

mylookup = TemplateLookup(directories=['html'], output_encoding='utf-8',
                          encoding_errors='replace')

class bibthek(object):

    def db(self):
        return mongo_db(cherrypy.session['username'])

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/books/All/series/variant1_order")

    @cherrypy.expose
    def books(self, shelf=None, sort_first=None, sort_second=None,
              _filter = '', book_id='new_book', book_type='book', view="books"):

        if sort_second == None:
            raise cherrypy.HTTPRedirect("/" + view +
                                        "/All/series/variant1_order")
        shelf = shelf.encode("latin-1").decode("utf-8")
        _filter = _filter.encode("latin-1").decode("utf-8")
        book = get_book_data(self.db(), book_id, book_type, shelf)
        user = mongo_user(cherrypy.session.id)
        sort1, sort2, active_sort, items = menu_data(self.db(), shelf, _filter,
                                                     sort_first, sort_second)
        filters = menu_filter(self.db(), shelf)
        mytemplate = mylookup.get_template("book.html")
        shelfs = self.db().shelfs(_filter)
        active_shelf = {}
        active_shelf['shelf'] = shelf
        active_shelf['#items'] = self.db().count_items(shelf, _filter)
        if view == 'covers':
            covers = self.db().covers(shelf, _filter)
        else:
            covers = None
        return mytemplate.render(items=items, book=book, shelfs=shelfs,
                                 active_shelf=active_shelf,
                                 sort1=sort1, sort2=sort2,
                                 active_sort=active_sort,
                                 active_filter=_filter, filters = filters,
                                 view=view, covers=covers, user=user)

    @cherrypy.expose
    def books2(self, shelf=None, sort_first=None, sort_second=None,
               _filter = '', book_id='new_book', book_type='book'):
        
        return self.books(shelf, sort_first, sort_second, _filter, book_id,
                          book_type, "books2")

    @cherrypy.expose
    def covers(self, shelf=None, sort_first=None, sort_second=None,
               _filter = '', book_id='new_book', book_type='book'):
        
        return self.books(shelf, sort_first, sort_second, _filter, book_id,
                          book_type, "covers")
    
    
    @cherrypy.expose
    def json_book(self, book_id, book_type='book', shelf='All'):
        book = get_book_data(self.db(), book_id, book_type, shelf)
        return json.dumps(book)

    @cherrypy.expose
    def autocomplete(self, field, query):
        if field in ['authors', 'artist', 'colorist', 'cover_artist', 'genre']:
            array = True
            ac_list = mongo_db.autocomplete(self.db(), query, field, array)
            return json.dumps(ac_list)
        if field in ['publisher', 'series', 'language', 'binding', 'shelf']:
            array = False
            ac_list = mongo_db.autocomplete(self.db(), query, field, array)
            return json.dumps(ac_list)

    @cherrypy.expose
    def menu(self, shelf='All'):
        mytemplate = mylookup.get_template("menu.html")
        series = self.db().series(shelf)
        shelfs = self.db().shelfs()
        return mytemplate.render(series=series, shelfs=shelfs)

    @cherrypy.expose
    def settings(self):
        user = mongo_user(cherrypy.session.id)
        mytemplate = mylookup.get_template("settings.html")
        return mytemplate.render(user=user)

    @cherrypy.expose
    def statistics(self, shelf=None, _filter = ''):
        if shelf == None:
            raise cherrypy.HTTPRedirect("/statistics/All")
        shelf = shelf.encode("latin-1").decode("utf-8")
        _filter = _filter.encode("latin-1").decode("utf-8")
        filters = menu_filter(self.db(), shelf)
        shelfs = self.db().shelfs(_filter)
        active_shelf = {}
        active_shelf['shelf'] = shelf
        active_shelf['#items'] = self.db().count_items(shelf, _filter)
        user = mongo_user(cherrypy.session.id)
        mytemplate = mylookup.get_template("statistics.html")
        return mytemplate.render(active_sort='', shelfs=shelfs,
                                 active_shelf=active_shelf,
                                active_filter=_filter, filters = filters,
                                user=user)

    @cherrypy.expose
    def json_statistic(self, shelf=None, _filter = '', _type = None):
        shelf = shelf.encode("latin-1").decode("utf-8")
        _filter = _filter.encode("latin-1").decode("utf-8")
        if _type.split('#')[0] in ['release_date', 'add_date']:
            labels, data = mongo_db.statistic_date_easy(self.db(), shelf,
                                                         _filter, _type)
        elif _type.split('#')[0] in ['start_date', 'finish_date']:
            labels, data = mongo_db.statistic_date_hard(self.db(), shelf,
                                                        _filter, _type)
        elif _type.split('#')[0] == 'pages_read':
            labels, data = mongo_db.statistic_pages_read(self.db(), shelf,
                                                        _filter, _type)
        elif _type.split('#')[0] == 'pages_book':
            labels, data = mongo_db.statistic_pages_book(self.db(), shelf,
                                                        _filter)
        return json.dumps({'data' : data, 'labels' : labels,
                           'canvas_id' : _type.split('#')[0] + '_chart'})

    @cherrypy.expose
    @cherrypy.tools.auth(user_role='admin')
    def admin(self):
        user = mongo_user(cherrypy.session.id)
        user_list = mongo_user_list()
        mytemplate = mylookup.get_template("admin.html")
        return mytemplate.render(user=user, user_list=user_list)

    @cherrypy.expose
    def change_email(self, password, email_new):
        if mongo_login(cherrypy.session['username'], password, None):
            mongo_change_email(cherrypy.session['username'], email_new)
            return json.dumps({'type' : 'success', 'error' : 'Email changed',
                              'email' : email_new})
        else:
            return json.dumps({'type' : 'danger', 'error' : 'Wrong Password'})
            

    @cherrypy.expose
    def change_pw(self, password_old, password_new):
        error = mongo_change_pw(cherrypy.session['username'], password_old,
                                password_new)
        if error == '0':
            raise cherrypy.HTTPRedirect("/logout")
        else:
            return json.dumps({'type' : 'danger', 'error' : error})

    @cherrypy.expose
    def delete_acc(self, password=None, username=None):
        allowed = False
        if username == None and password != None:
            username = cherrypy.session['username']
            allowed = mongo_login(username, password, None)
        elif (mongo_user(cherrypy.session.id)['role'] == 'admin' and
             username != None):
            allowed = True
        if  allowed:
            del_all_books(username)
            mongo_user_del(username)
            if password != None:
                cherrypy.lib.sessions.expire()
                raise cherrypy.HTTPRedirect("/")
            else:
                return json.dumps({'type' : 'success',
                                   'error' : 'Account deleted'})
        else:
            return json.dumps({'type' : 'danger', 'error' : 'Wrong Password'})

    @cherrypy.expose
    @cherrypy.tools.auth(user_role='admin')
    def reset_pw(self, username):
        return json.dumps({'type' : 'success',
                           'error' : 'Please tell ' + username +
                           ' the new password: "' +
                           mongo_reset_pw(username) + '"'})

    @cherrypy.expose
    def import_books(self, data_upload=None, separator=None):
        if data_upload == None or data_upload.file == None:
            user = mongo_user(cherrypy.session.id)
            mytemplate = mylookup.get_template("import.html")
            return mytemplate.render(user=user)
        else:
            data = data_upload
            username = cherrypy.session['username']
            data, error = import_file(data, username, separator)
            if error != '0':
                return json.dumps({"type" : "danger", "error" : error})
            else:
                for row in data:
                    self.db().insert(row)           
                return json.dumps({"type" : "success",
                                   "error" : 'Upload complete'})

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
        book_id, new, error = save_book_data(self.db(), params)
        return json.dumps({'book_id' : book_id, 'new' : new, 'error' : error})

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
            isbn = self.db().get_by_id(book_id)['isbn']
        raise cherrypy.HTTPRedirect("https://www.goodreads.com/search?" +
                                    "utf8=%E2%9C%93&query=" + isbn)

    @cherrypy.expose
    def delete(self, book_id):
        del_book(self.db(), book_id)
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def delete_all(self):
        del_all_books(cherrypy.session['username'])
        return json.dumps({"type" : "success", "error" : "All books deleted"})
    
    @cherrypy.expose
    def logout(self):
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    @cherrypy.tools.auth(required = False)
    def register(self, secret = '', username = '', password = '', mail = ''):
        if password and username is not '':
            error = mongo_add_user(username, password, mail,
                                   cherrypy.session.id)
        else:
            mytemplate = mylookup.get_template("register.html")
            return mytemplate.render()
        if error == '0':
            raise cherrypy.HTTPRedirect("/")
        else:
            return error

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
    cherrypy.quickstart(bibthek(), '/', 'app.conf')
