fieldnames=['authors', 'description', 'release_date', 'genre', 'isbn',
            'series', 'order', 'pages', 'language', 'title', 'front',
            'publisher', 'binding', 'finish_date', 'start_date', 'add_date',
            'abdoned', 'shelf', 'type', 'colorist', 'artist', 'book_id']

articles = ["le","la","les","l","un","une","des","a","the","der","die",
            "das","ein","eine","el","los","una"]

name_fields=['authors', 'colorist', 'artist']

date_fields=['release_date', 'finish_date', 'start_date', 'add_date']

def book_empty_default():
    book_empty = {name : '' for name in fieldnames}
    book_empty['front'] =  'icons/circle-x.svg'
    book_empty['_id'] = 'new_book'
    book_empty['type'] = 'book'
    book_empty['reading_stats'] = None
    return book_empty
