from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
import json
from requests import get

from mongo_db import mongo_db
from mongo_db import mongo_add_user, mongo_user, mongo_login
from variables import fieldnames
from get_data import google_books_data

mylookup = TemplateLookup(directories=['html'], output_encoding='utf-8', encoding_errors='replace')

book_empty = {name : '' for name in fieldnames}
book_empty['front'] =  'icons/circle-x.svg'
book_empty['_id'] = 'new_book'

class bibthek(object):

    @cherrypy.expose
    def index(self, json_data = False):
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
        if json_data:
            return json.dumps(book_empty)
        else:
            mytemplate = mylookup.get_template("book.html")
            print("testtest!!!!!!!!\n")
            field = {'title' : 1, 'series': 1}
            series = self.mongo.series()
            return mytemplate.render(series=series, book=book_empty, new=True)

    @cherrypy.expose
    def book(self, book_id, json_data = False):
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
        print("testtest!!!!!!!!\n")
        book = self.mongo.get_by_id(book_id)

        for k, v in book_empty.items():
            try:
                book[k]
            except:
                book[k] = v
            if isinstance(book[k], list) : book[k] = ' & '.join(book[k])

        book['_id'] = str(book['_id'])

        if json_data:
            return json.dumps(book)
        else:
            series = self.mongo.series()
            mytemplate = mylookup.get_template("book.html")
            return mytemplate.render(series=series, book=book, new=False)

    @cherrypy.expose
    def save(self, **params):
        if mongo_user(cherrypy.session.id) == None:
            raise cherrypy.HTTPRedirect("/login")
        mongo.update(params)

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
        #return json.dumps(gr_id)
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
