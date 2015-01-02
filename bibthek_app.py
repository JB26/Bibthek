from mako.template import Template
from mako.lookup import TemplateLookup
import cherrypy
import json
from requests import get

from mongo_db import mongo_delete_by_id
from mongo_db import mongo_series
from mongo_db import mongo_update
from mongo_db import mongo_ids
from mongo_db import mongo_get_by_id
from variables import fieldnames
from get_data import google_books_data

mylookup = TemplateLookup(directories=['html'], output_encoding='utf-8', encoding_errors='replace')

ids = mongo_ids()

book_empty = {name : '' for name in fieldnames}
book_empty['front'] =  'icons/circle-x.svg'
book_empty['_id'] = 'new_book'

class bibthek(object):
    @cherrypy.expose
    def index(self, json_data = False):
        if json_data:
            return json.dumps(book_empty)
        else:
            mytemplate = mylookup.get_template("book.html")
            print("testtest!!!!!!!!\n")
            field = {'title' : 1, 'series': 1}
            series = mongo_series()
            return mytemplate.render(series=series, book=book_empty, new=True)

    @cherrypy.expose
    def book(self, book_id, json_data = False):
        print("testtest!!!!!!!!\n")
        book = mongo_get_by_id(book_id)

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
            series = mongo_series()
            mytemplate = mylookup.get_template("book.html")
            return mytemplate.render(series=series, book=book, new=False)

    @cherrypy.expose
    def save(self, **params):
        mongo_update(params)

    @cherrypy.expose
    def new_isbn(self, isbn):
        book = google_books_data(isbn)
        return json.dumps(book)

    @cherrypy.expose
    def gr_id(self, book_id='', isbn=''):
        if book_id != '':
            book = mongo_get_by_id(book_id)
            gr_id = {'gr_id' : get('https://www.goodreads.com/book/isbn_to_id/' + book['isbn']  + '?key=Fyl3BYyRgNUZAoD1M9rQ').text}
        elif isbn != '':
            gr_id = {'gr_id' : get('https://www.goodreads.com/book/isbn_to_id/' + isbn  + '?key=Fyl3BYyRgNUZAoD1M9rQ').text}
        return json.dumps(gr_id)

    @cherrypy.expose
    def delete(self, book_id):
        mongo_delete_by_id(book_id)
        raise cherrypy.HTTPRedirect("/")

if __name__ == '__main__':
    cherrypy.quickstart(bibthek(), '/', 'app.conf')
