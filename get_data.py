from requests import get
from import_cleaner import date_clean

def google_books_data(isbn):
    r = get('https://www.googleapis.com/books/v1/volumes?q=isbn:' + isbn)
    gb_book = r.json()
    book = {}
    if 'authors' in gb_book['items'][0]['volumeInfo'] : book['authors'] = gb_book['items'][0]['volumeInfo']['authors']
    if 'description' in gb_book['items'][0]['volumeInfo'] : book['description'] = gb_book['items'][0]['volumeInfo']['description']
    if 'publishedDate' in gb_book['items'][0]['volumeInfo'] :  book['release_date'] = date_clean(gb_book['items'][0]['volumeInfo']['publishedDate'])
    if 'pageCount' in gb_book['items'][0]['volumeInfo'] : book['pages'] = gb_book['items'][0]['volumeInfo']['pageCount']
    if 'title' in gb_book['items'][0]['volumeInfo'] : book['title'] = gb_book['items'][0]['volumeInfo']['title']
    return book
