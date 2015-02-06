names = ['authors', 'description', 'release_date', 'genre', 'isbn',
         'series', 'order', 'pages', 'language', 'title', 'front',
         'publisher', 'binding', 'add_date', 'shelf', 'type', 'colorist',
         'artist', 'cover_artist', 'book_id', 'form']

reading_stats_names = ['finish_date', 'start_date', 'abdoned']

fieldnames = names + reading_stats_names

dbnames = names + ['reading_stats', 'read_count', 'series_complete']

articles = ["le","la","les","l","un","une","des","a","the","der","die",
            "das","ein","eine","el","los","una"]

name_fields=['authors', 'colorist', 'artist', 'cover_artist']

date_fields=['release_date', 'finish_date', 'start_date', 'add_date']

def book_empty_default():
    book_empty = {name : '' for name in fieldnames}
    book_empty['front'] =  'static/icons/circle-x.svg'
    book_empty['_id'] = 'new_book'
    book_empty['type'] = 'book'
    book_empty['reading_stats'] = None
    book_empty['form'] = 'Physical'
    return book_empty
