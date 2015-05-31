"""Declare Variablenames"""
class Variables:
    """Static variable names"""
    def __init__(self):
        self.names = ['authors', 'description', 'release_date', 'genre',
                      'isbn', 'series', 'order_nr', 'pages', 'language',
                      'title', 'front', 'publisher', 'add_date', 'shelf',
                      'type', 'colorist', 'artist', 'cover_artist', 'narrator',
                      'form']
        self.reading_stats_names = ['finish_date', 'start_date', 'abdoned']
        self.fieldnames = self.names + self.reading_stats_names
        self.dbnames = self.names + ['reading_stats', 'read_count',
                                     'series_complete']
        self.articles = ["le", "la", "les", "l", "un", "une", "des", "a",
                         "the", "der", "die", "das", "ein", "eine", "el",
                         "los", "una"]
        self.name_fields = ['authors', 'colorist', 'artist', 'cover_artist',
                            'narrator']
        self.date_fields = ['release_date', 'finish_date', 'start_date',
                            'add_date']

VARIABLES = Variables()

def book_empty_default():
    """Default empty book"""
    book_empty = {name : '' for name in VARIABLES.fieldnames}
    book_empty['front'] = 'static/icons/circle-x.svg'
    book_empty['_id'] = 'new_book'
    book_empty['type'] = 'book'
    book_empty['reading_stats'] = None
    return book_empty
