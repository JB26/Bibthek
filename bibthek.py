"""Webapp for storing what books you own and have already read"""
from mako.lookup import TemplateLookup
MY_LOOKUP = TemplateLookup(directories=['html'], output_encoding='utf-8',
                           encoding_errors='replace')
import cherrypy
from cherrypy.lib import static
import json
import os
LOCAL_DIR = os.path.dirname(__file__)
ABS_DIR = os.path.join(os.getcwd(), LOCAL_DIR)
import configparser
CONFIG = configparser.ConfigParser()
CONFIG.read('app.conf')
import gettext
gettext.translation('messages', localedir='translations',
                    languages=[CONFIG['Language']['language'][1:-1]],
                    fallback=True).install()

import lib.db_sql as db_sql
import lib.db_books as db_books
import lib.db_users as db_users
import lib.gen_thumbs as gen_thumbs
from lib.book_data import get_book_data, save_book_data
from lib.get_data import google_books_data
from lib.import_data import import_file
from lib.export_data import export_csv, export_cover_csv
from lib.del_books import del_all_books, del_book
import lib.auth as auth
from lib.menu_data import menu_data, menu_filter
from lib.variables import VARIABLES

cherrypy.tools.auth = cherrypy.Tool('before_handler', auth.check_auth)
cherrypy.tools.rights = cherrypy.Tool('before_handler', auth.check_rights)

def args_to_list(args):
    """Convert given args to a list"""
    if args == None:
        args = ('', )
    else:
        if not isinstance(args, tuple):
            args = [args]
        else:
            args = list(args)
    active_filters = []
    for _filter in args:
        active_filters.append(_filter.encode("latin-1").decode("utf-8"))
    return active_filters

class Bibthek(object):
    """The main cherrypy class"""

    def __init__(self):
        """Init class"""
        self.error = None
        self.login_ref = None

    @cherrypy.expose
    def index(self):
        """Redirect to the standard view"""
        raise cherrypy.HTTPRedirect("/view/" +
                                    cherrypy.session.get('username'))

    @cherrypy.expose
    @cherrypy.tools.auth(required=False)
    @cherrypy.tools.rights()
    def view(self, view_user, view='books', sort_first=None, sort_second=None,
             *args, **kw):
        """Return a webpage with a list of your books that match your
        criterias. The page also contains information about the book
        requested by 'book_id'
        """
        if sort_second == None:
            raise cherrypy.HTTPRedirect("/view/" + view_user  + "/" + view +
                                        "/series/variant1_order")
        if 'book_id' not in kw:
            kw['book_id'] = 'new_book'
        active_filters = args_to_list(args)
        book = get_book_data(view_user, kw['book_id'])
        user = db_users.user_by_name(cherrypy.session.get('username'))
        sort1, sort2, active_sort, items = menu_data(view_user,
                                                     active_filters,
                                                     sort_first, sort_second)
        filters = menu_filter(view_user, active_filters)
        mytemplate = MY_LOOKUP.get_template("book.html")
        items_count = db_books.count_items(view_user, active_filters)
        if view in ['covers', 'covers2']:
            covers = db_books.covers(view_user, active_filters)
        else:
            covers = None
        error = self.error
        self.error = None
        return mytemplate.render(items=items, book=book,
                                 sort1=sort1, sort2=sort2,
                                 active_sort=active_sort,
                                 items_count=items_count,
                                 active_filter=active_filters, filters=filters,
                                 view=view, covers=covers,
                                 user=user, view_user=view_user,
                                 error=error)

    @cherrypy.expose
    @cherrypy.tools.auth(required=False)
    @cherrypy.tools.rights()
    def json_book(self, view_user, book_id):
        """Return information about a book in json format"""
        book = get_book_data(view_user, book_id)
        return json.dumps(book)

    @cherrypy.expose
    @cherrypy.tools.auth(required=False)
    def thumbnails(self, folder1, folder2, folder3, thumbnail):
        """Genarate thumbnail and return it"""
        thumbnail = folder1 + '/' + folder2 + '/' + folder3 + '/' + thumbnail
        file_name = gen_thumbs.gen_thumbs(thumbnail)
        path = os.path.join(ABS_DIR, file_name)
        return static.serve_file(path)

    @cherrypy.expose
    def autocomplete(self, field, query):
        """Returns an array (json format) of suggestions with names that are allready
        in the database
        """
        username = cherrypy.session.get('username')
        array = None
        if field in ['authors', 'artist', 'colorist', 'cover_artist', 'genre']:
            array = True
        elif field in ['publisher', 'series', 'language', 'form', 'shelf']:
            array = False
        if array != None:
            ac_list = db_books.autocomplete(username, query, field, array)
            return json.dumps(ac_list)

    @cherrypy.expose
    @cherrypy.tools.auth(required=False)
    def reading_stats(self, i, start, finish, abdoned=False):
        """Returns html that will be inserted into the main page. Containing
         information about how and when a book was read
         """
        if abdoned == 'false':
            abdoned = False
        elif abdoned == 'true':
            abdoned = True
        mytemplate = MY_LOOKUP.get_template("reading_stats.html")
        reading_stats = {'start_date' : start, 'finish_date' : finish,
                         'abdoned' : abdoned}
        return mytemplate.render(i=i, reading_stats=reading_stats)

    @cherrypy.expose
    def settings(self):
        """Returns a settings page (Change PW, mail; Delete Account)"""
        user = db_users.user_by_name(cherrypy.session.get('username'))
        mytemplate = MY_LOOKUP.get_template("settings.html")
        return mytemplate.render(user=user, view_user=user['username'])

    @cherrypy.expose
    @cherrypy.tools.auth(required=False)
    @cherrypy.tools.rights()
    def statistics(self, view_user, *args):
        """Returns a page containing statistics about your books"""
        active_filters = args_to_list(args)
        filters = menu_filter(view_user, active_filters)
        user = db_users.user_by_name(cherrypy.session.get('username'))
        mytemplate = MY_LOOKUP.get_template("statistics.html")
        return mytemplate.render(active_sort='',
                                 active_filter=active_filters, filters=filters,
                                 user=user, view_user=view_user)

    @cherrypy.expose
    @cherrypy.tools.auth(required=False)
    @cherrypy.tools.rights()
    def json_statistic(self, view_user, _type=None, *args):
        """Returns statistical data about your books in json form"""
        active_filters = args_to_list(args)
        if _type.split('#')[0] in ['release_date', 'add_date', 'start_date',
                                   'finish_date']:
            labels, data = db_books.statistic_date(view_user, active_filters,
                                                   _type)
        elif _type.split('#')[0] == 'pages_read':
            labels, data = db_books.statistic_pages_read(view_user,
                                                         active_filters, _type)
        elif _type.split('#')[0] == 'pages_book':
            labels, data = db_books.statistic_pages_book(view_user,
                                                         active_filters)
        return json.dumps({'data' : data, 'labels' : labels,
                           'canvas_id' : _type.split('#')[0] + '_chart'})

    @cherrypy.expose
    @cherrypy.tools.auth(user_role='admin')
    def admin(self):
        """Administration"""
        user = db_users.user_by_name(cherrypy.session.get('username'))
        user_list = db_users.user_list()
        mytemplate = MY_LOOKUP.get_template("admin.html")
        return mytemplate.render(user=user, user_list=user_list,
                                 view_user=user['username'])

    @cherrypy.expose
    def privacy(self, status):
        """Changes your privacy status"""
        if status in ['private', 'public']:
            db_users.privacy(cherrypy.session.get('username'), status)
            raise cherrypy.HTTPRedirect("/settings")

    @cherrypy.expose
    def change_email(self, password, email_new):
        """Changes your email"""
        if db_users.login(cherrypy.session.get('username'), password, None):
            db_users.change_email(cherrypy.session.get('username'), email_new)
            return json.dumps({'type' : 'success',
                               'error' : _('Email changed'),
                               'email' : email_new})
        else:
            return json.dumps({'type' : 'danger',
                               'error' : _('Wrong password')})

    @cherrypy.expose
    def change_pw(self, password_old, password_new):
        """Changes your password"""
        error = db_users.change_pw(cherrypy.session.get('username'),
                                   password_old, password_new)
        if error == '0':
            raise cherrypy.HTTPRedirect("/logout")
        else:
            return json.dumps({'type' : 'danger', 'error' : error})

    @cherrypy.expose
    def delete_acc(self, password=None, username=None, _json='false'):
        """Deletes your account"""
        allowed = False
        if username == None and password != None:
            username = cherrypy.session.get('username')
            allowed = db_users.login(username, password, None)
        elif (db_users.user_by_name(cherrypy.session.get('username'))['role'] ==
              'admin' and username != None):
            allowed = True
        if  allowed:
            del_all_books(username)
            db_users.user_del(username)
            if password != None:
                cherrypy.lib.sessions.expire()
                if _json == 'false':
                    raise cherrypy.HTTPRedirect("/")
                else:
                    print('del')
                    return json.dumps({'type' : 'success',
                                       'error' : _('Your account is deleted')})
            else:
                return json.dumps({'type' : 'success',
                                   'error' : _('Account deleted')})
        else:
            return json.dumps({'type' : 'danger',
                               'error' : _('Wrong password')})

    @cherrypy.expose
    @cherrypy.tools.auth(user_role='admin')
    def reset_pw(self, username):
        """Resets a password for a given user (only an admin can do this)"""
        return json.dumps({'type' : 'success',
                           'error' : _('Please tell %s the new password: "%s"')
                                       % (username,
                                          db_users.reset_pw(username))})

    @cherrypy.expose
    def import_books(self, data_upload=None, separator=None):
        """Retunrs a page where you can upload your books or export them.
        If data is uploaded, it gets imported
        """
        username = cherrypy.session.get('username')
        if data_upload == None or data_upload.file == None:
            user = db_users.user_by_name(username)
            mytemplate = MY_LOOKUP.get_template("import.html")
            return mytemplate.render(user=user, view_user=user['username'])
        else:
            data = data_upload
            data, error = import_file(data, username, separator)
            if error != '0':
                return json.dumps({"type" : "danger", "error" : error})
            else:
                db_books.insert_many_new(username, data)
                return json.dumps({"type" : "success",
                                   "error" : _('Upload complete')})

    @cherrypy.expose
    def export(self, _type):
        """Export your data"""
        data = db_books.get_all(cherrypy.session.get('username'))
        if _type == 'csv':
            file_name = export_csv(data, cherrypy.session.get('username'))
        elif _type == 'cover_csv':
            file_name = export_cover_csv(data, cherrypy.session.get('username'))
        path = os.path.join(ABS_DIR, file_name)
        return static.serve_file(path, "application/x-download",
                                 "attachment", os.path.basename(path))

    @cherrypy.expose
    def save(self, **params):
        """Upload and save changes to a book"""
        username = cherrypy.session.get('username')
        book_id, error = save_book_data(username, params)
        url = str(cherrypy.request.headers.elements('Referer')[0])
        url = url.rsplit("?")[0] + "?book_id=" + book_id
        if error == '0':
            self.error = {'type' : 'success', 'error' : _("Book saved!")}
        else:
            self.error = {'type' : 'danger', 'error' : error}
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose
    def batch_edit(self, edit, old_name, new_name):
        """Edit multiple books"""
        username = cherrypy.session.get('username')
        if edit in ['series'] + VARIABLES.name_fields:
            db_books.change_field(username, edit, old_name, new_name)
            raise cherrypy.HTTPRedirect(str(cherrypy.request.headers
                                            .elements('Referer')[0]))

    @cherrypy.expose
    def star_series(self, series, status):
        """Mark a series as complete"""
        db_books.star_series(cherrypy.session.get('username'), series, status)
        return '0'

    @cherrypy.expose
    def new_isbn(self, isbn):
        """Return google books data for a given ISBN in json format"""
        book = google_books_data(isbn)
        return json.dumps(book)

    @cherrypy.expose
    def delete(self, book_id):
        """Delete a book"""
        del_book(cherrypy.session.get('username'), book_id)
        url = str(cherrypy.request.headers.elements('Referer')[0]).rsplit("?")[0]
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose
    def delete_all(self):
        """Delete all your books"""
        del_all_books(cherrypy.session.get('username'))
        return json.dumps({"type" : "success",
                           "error" : _("All books deleted")})

    @cherrypy.expose
    def logout(self):
        """Logout"""
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def logout_all(self):
        """Logout all your sessions"""
        db_users.logout_all(cherrypy.session.get('username'))
        cherrypy.lib.sessions.expire()
        raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    @cherrypy.tools.auth(required=False)
    def register(self, secret_key='', username='', password='', mail=''):
        """Register an account"""
        reg_status = cherrypy.request.app.config['Registration']
        if reg_status['registration'] in ['open', 'secret']:
            if password and username is not '':
                if (reg_status['registration'] == 'open' or
                    reg_status['secret_key'] == secret_key):
                    error = db_users.add_user(username, password, mail,
                                              cherrypy.session.id)
                else:
                    error = _('Wrong secret key')
            else:
                mytemplate = MY_LOOKUP.get_template("register.html")
                return mytemplate.render(reg_status=reg_status['registration'])
            if error == '0':
                raise cherrypy.HTTPRedirect("/")
            else:
                return error
        else:
            return _('Registration closed')

    @cherrypy.expose
    @cherrypy.tools.auth(required=False)
    def login(self, username='', password=''):
        """Login"""
        if username == '' and password == '':
            try:
                url = str(cherrypy.request.headers.elements('Referer')[0])
                url = url.split('/')[3]
                if url not in  ["register", "logout", "logout_all"]:
                    self.login_ref = url
                else:
                    self.login_ref = None
            except IndexError:
                self.login_ref = None
            mytemplate = MY_LOOKUP.get_template("login.html")
            return mytemplate.render()
        elif db_users.login(username, password, cherrypy.session.id):
            db_sql.init_books(username)
            #Make sure the session ID stops changing
            cherrypy.session['username'] = username
            if self.login_ref != None:
                url = self.login_ref
            else:
                url = "/"
            raise cherrypy.HTTPRedirect(url)
        else:
            return _('Login problem')

if __name__ == '__main__':
    db_sql.init_users()
    cherrypy.quickstart(Bibthek(), '/', 'app.conf')
