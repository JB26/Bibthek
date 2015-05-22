from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
from cherrypy.lib import static
import json
from requests import get
from urllib import request

import os
localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)

import lib.db_sql as db_sql
from lib.book_data import get_book_data, save_book_data
from lib.get_data import google_books_data
from lib.import_data import import_file
from lib.export_data import export_csv, export_cover_csv
from lib.del_books import del_all_books, del_book
import lib.auth as auth
import lib.rights as rights
from lib.menu_data import menu_data, menu_filter
from lib.variables import name_fields

mylookup = TemplateLookup(directories=['html'], output_encoding='utf-8',
                          encoding_errors='replace')

class bibthek(object):

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/view/" + cherrypy.session.get('username'))

    @cherrypy.expose
    @cherrypy.tools.auth(required = False)
    @cherrypy.tools.rights()
    def view(self, view_user, view='books', shelf=None, sort_first=None,
             sort_second=None, _filter = '', book_id='new_book',
             book_type='book'):
        return self.books(view_user, view, shelf, sort_first, sort_second,
                          _filter, book_id, book_type)

    def books(self, view_user, view, shelf, sort_first, sort_second, _filter,
              book_id, book_type):
        if sort_second == None:
            raise cherrypy.HTTPRedirect("/view/" + view_user  + "/" + view +
                                        "/All/series/variant1_order")
        shelf = shelf.encode("latin-1").decode("utf-8")
        _filter = _filter.encode("latin-1").decode("utf-8") 
        book = get_book_data(view_user, book_id, book_type, shelf)
        user = db_sql.user_by_name(cherrypy.session.get('username'))
        sort1, sort2, active_sort, items = menu_data(view_user, shelf,
                                                     _filter,
                                                     sort_first, sort_second)
        filters = menu_filter(view_user, shelf)
        mytemplate = mylookup.get_template("book.html")
        shelfs = db_sql.shelfs(view_user, _filter)
        active_shelf = {}
        active_shelf['shelf'] = shelf
        active_shelf['#items'] = db_sql.count_items(view_user, shelf, _filter)
        if view in ['covers', 'covers2']:
            covers = db_sql.covers(view_user, shelf, _filter)
        else:
            covers = None
        try:
            error = self.error
            self.error = None
        except AttributeError:
            error = None
        return mytemplate.render(items=items, book=book, shelfs=shelfs,
                                 active_shelf=active_shelf,
                                 sort1=sort1, sort2=sort2,
                                 active_sort=active_sort,
                                 active_filter=_filter, filters = filters,
                                 view=view, covers=covers,
                                 user=user, view_user=view_user,
                                 error=error)
    
    @cherrypy.expose
    @cherrypy.tools.auth(required = False)
    @cherrypy.tools.rights()
    def json_book(self, view_user, book_id, book_type='book', shelf='All'):
        shelf = request.url2pathname(shelf)
        book = get_book_data(view_user, book_id, book_type, shelf)
        return json.dumps(book)

    

    @cherrypy.expose
    def autocomplete(self, field, query):
        username = cherrypy.session.get('username')
        array = None
        if field in ['authors', 'artist', 'colorist', 'cover_artist', 'genre']:
            array = True
        elif field in ['publisher', 'series', 'language', 'binding', 'shelf']:
            array = False
        if array != None:
            ac_list = db_sql.autocomplete(username, query, field, array)
            return json.dumps(ac_list)

    @cherrypy.expose
    @cherrypy.tools.auth(required = False)
    @cherrypy.tools.rights()
    def reading_stats(self, view_user, i, start, finish, abdoned = False):
        if abdoned == 'false':
            abdoned = False
        elif abdoned == 'true':
            abdoned = True
        mytemplate = mylookup.get_template("reading_stats.html")
        reading_stats = {'start_date' : start, 'finish_date' : finish,
                         'abdoned' : abdoned}
        return mytemplate.render(i=i, reading_stats=reading_stats)

    @cherrypy.expose
    def settings(self):
        user = db_sql.user_by_name(cherrypy.session.get('username'))
        mytemplate = mylookup.get_template("settings.html")
        return mytemplate.render(user=user, view_user = user['username'])

    @cherrypy.expose
    @cherrypy.tools.auth(required = False)
    @cherrypy.tools.rights()
    def statistics(self, view_user, shelf=None, _filter = ''):
        if shelf == None:
            raise cherrypy.HTTPRedirect("/statistics/" + view_user  + "/All")
        shelf = shelf.encode("latin-1").decode("utf-8")
        _filter = _filter.encode("latin-1").decode("utf-8")
        filters = menu_filter(view_user, shelf)
        shelfs = db_sql.shelfs(view_user, _filter)
        active_shelf = {}
        active_shelf['shelf'] = shelf
        active_shelf['#items'] = db_sql.count_items(view_user, shelf, _filter)
        user = db_sql.user_by_name(cherrypy.session.get('username'))
        mytemplate = mylookup.get_template("statistics.html")
        return mytemplate.render(active_sort='', shelfs=shelfs,
                                 active_shelf=active_shelf,
                                active_filter=_filter, filters = filters,
                                user=user, view_user=view_user)

    @cherrypy.expose
    @cherrypy.tools.auth(required = False)
    @cherrypy.tools.rights()
    def json_statistic(self, view_user, shelf=None, _filter = '', _type = None):
        shelf = shelf.encode("latin-1").decode("utf-8")
        _filter = _filter.encode("latin-1").decode("utf-8")
        if _type.split('#')[0] in ['release_date', 'add_date', 'start_date',
                                   'finish_date']:
            labels, data = db_sql.statistic_date(view_user, shelf, _filter,
                                                 _type)
        elif _type.split('#')[0] == 'pages_read':
            labels, data = db_sql.statistic_pages_read(view_user,
                                                         shelf, _filter, _type)
        elif _type.split('#')[0] == 'pages_book':
            labels, data = db_sql.statistic_pages_book(view_user,
                                                         shelf, _filter)
        return json.dumps({'data' : data, 'labels' : labels,
                           'canvas_id' : _type.split('#')[0] + '_chart'})

    @cherrypy.expose
    @cherrypy.tools.auth(user_role='admin')
    def admin(self):
        user = db_sql.user_by_name(cherrypy.session.get('username'))
        user_list = db_sql.user_list()
        mytemplate = mylookup.get_template("admin.html")
        return mytemplate.render(user=user, user_list=user_list,
                                 view_user=user['username'])

    @cherrypy.expose
    def privacy(self, status):
        if status in ['private', 'public']:
            db_sql.privacy(cherrypy.session.get('username'), status)
            raise cherrypy.HTTPRedirect("/settings")

    @cherrypy.expose
    def change_email(self, password, email_new):
        if db_sql.login(cherrypy.session.get('username'), password, None):
            db_sql.change_email(cherrypy.session.get('username'), email_new)
            return json.dumps({'type' : 'success', 'error' : 'Email changed',
                              'email' : email_new})
        else:
            return json.dumps({'type' : 'danger', 'error' : 'Wrong Password'})
            

    @cherrypy.expose
    def change_pw(self, password_old, password_new):
        error = db_sql.change_pw(cherrypy.session.get('username'),
                                 password_old, password_new)
        if error == '0':
            raise cherrypy.HTTPRedirect("/logout")
        else:
            return json.dumps({'type' : 'danger', 'error' : error})

    @cherrypy.expose
    def delete_acc(self, password=None, username=None):
        allowed = False
        if username == None and password != None:
            username = cherrypy.session.get('username')
            allowed = db_sql.login(username, password, None)
        elif (db_sql.user_by_name(cherrypy.session.get('username'))['role'] ==
              'admin' and username != None):
            allowed = True
        if  allowed:
            del_all_books(username)
            db_sql.user_del(username)
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
                           db_sql.reset_pw(username) + '"'})

    @cherrypy.expose
    def import_books(self, data_upload=None, separator=None):
        username = cherrypy.session.get('username')
        if data_upload == None or data_upload.file == None:
            user = db_sql.user_by_name(username)
            mytemplate = mylookup.get_template("import.html")
            return mytemplate.render(user=user, view_user=user['username'])
        else:
            data = data_upload
            data, error = import_file(data, username, separator)
            if error != '0':
                return json.dumps({"type" : "danger", "error" : error})
            else:
                db_sql.insert_many_new(username, data)
                return json.dumps({"type" : "success",
                                   "error" : 'Upload complete'})

    @cherrypy.expose
    def export(self, _type):
        data = db_sql.get_all(cherrypy.session.get('username'))
        if _type == 'csv':
            file_name = export_csv(data, cherrypy.session.get('username'))
        elif _type == 'cover_csv':
            file_name = export_cover_csv(data, cherrypy.session.get('username'))
        path = os.path.join(absDir, file_name)
        return static.serve_file(path, "application/x-download",
                                 "attachment", os.path.basename(path))
        
    @cherrypy.expose
    def save(self, **params):
        username = cherrypy.session.get('username')
        book_id, new, error = save_book_data(username, params)
        url = str(cherrypy.request.headers.elements('Referer')[0])
        url = url.rsplit("?")[0] + "?book_id=" + book_id
        if error == '0':
            self.error = {'type' : 'success', 'error' : "Book saved!"}
        else:
            self.error = {'type' : 'danger', 'error' : error}
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose
    def batch_edit(self, edit, old_name, new_name):
        username = cherrypy.session.get('username')
        if edit in ['series'] + name_fields:
            db_sql.change_field(username, edit, old_name, new_name)
            raise cherrypy.HTTPRedirect( str(cherrypy.request.headers
                                            .elements('Referer')[0]) )

    @cherrypy.expose
    def star_series(self, series, status):
        db_sql.star_series(cherrypy.session.get('username'), series, status)
        return '0'

    @cherrypy.expose
    def new_isbn(self, isbn):
        book = google_books_data(isbn)
        return json.dumps(book)

    @cherrypy.expose
    def delete(self, book_id):
        del_book(cherrypy.session.get('username'), book_id)
        url = str(cherrypy.request.headers.elements('Referer')[0]).rsplit("?")[0]
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose
    def delete_all(self):
        del_all_books(cherrypy.session.get('username'))
        return json.dumps({"type" : "success", "error" : "All books deleted"})

    @cherrypy.expose
    def logout(self):
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def logout_all(self):
        db_sql.logout_all(cherrypy.session.get('username'))
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    @cherrypy.tools.auth(required = False)
    def register(self, secret = '', username = '', password = '', mail = ''):
        if password and username is not '':
            error = db_sql.add_user(username, password, mail,
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
            try:
                url = str(cherrypy.request.headers.elements('Referer')[0])
                url = url.split('/')[3]
                if url not in  ["register", "logout", "logout_all"]:
                    self.login_ref = url
            except IndexError:
                pass
            mytemplate = mylookup.get_template("login.html")
            return mytemplate.render()
        elif db_sql.login(username, password, cherrypy.session.id):
            #Make sure the session ID stops changing
            cherrypy.session['username'] = username
            try:
                url = self.login_ref
            except AttributeError:
                url = "/"
            raise cherrypy.HTTPRedirect(url)
        else:
            return "Login problem"

if __name__ == '__main__':
    db_sql.init_users()
    cherrypy.quickstart(bibthek(), '/', 'app.conf')
