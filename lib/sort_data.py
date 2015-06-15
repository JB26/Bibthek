"""Sort Books"""
from operator import itemgetter
import configparser
CONFIG = configparser.ConfigParser()
CONFIG.read('app.conf')
import locale
locale.setlocale(locale.LC_ALL, CONFIG['Language']['sort_locale'][1:-1])

from lib.variables import VARIABLES

def sorted_filters(data):
    """Sort filters"""
    return library_sorted(data, 'name', False)

def sorted_apg(data, sort_by_order, sort_first):
    """Sort author and similar"""
    temp = []
    for row in data:
        for book in row['books']:
            if 'order_nr' in book and book['order_nr'] != '':
                book['order_nr'] = book['order_nr'][0:4]
        row['books'] = library_sorted(row['books'], 'title', sort_by_order)
        if sort_first in VARIABLES.name_fields:
            find_surname = row['_id'].rsplit(maxsplit=1)
            if len(find_surname) == 2:
                temp.append(find_surname[1] + ' ' + find_surname[0])
            elif len(find_surname) == 1:
                temp.append(row['_id'])
        else:
            temp.append(row['_id'])
        temp[-1] = locale.strxfrm(temp[-1])
    return [i[1] for i in sorted(zip(temp, data), key=itemgetter(0))]

def sorted_titles(data, field, variant='year'):
    """Sort titles"""
    sort_by_order = False
    for row in data:
        if 'order_nr' in row and row['order_nr'] != '':
            if variant == 'year':
                row['order_nr'] = row['order_nr'][0:4]
            sort_by_order = True
    return library_sorted(data, field, sort_by_order)

def sorted_series(data, variant):
    """Sort series"""
    data = library_sorted(data, '_id', False)  #Sort series titles
    for series in data:  #Sort book titles in series
        if series['sub_items']:
            if variant.split('_')[1] == 'year':
                for row in series['books']:
                    if 'order_nr' in row and row['order_nr'] != '':
                        row['order_nr'] = row['order_nr'][0:4]
            series['books'] = library_sorted(series['books'], 'title', True)
    return data

def library_sorted(data, field, sort_by_order):
    """Library sorting"""
    temp = []
    for row in data:
        if sort_by_order:
            temp.append(str(row['order_nr']) + " ")
        else:
            temp.append('')
            find_article = row[field].split(maxsplit=1)
            if len(find_article) == 2 and (find_article[0].lower() in
                                           VARIABLES.articles):
                temp[-1] = temp[-1] + find_article[1] + find_article[0]
        temp[-1] = locale.strxfrm(temp[-1] + row[field])
    return [i[1] for i in sorted(zip(temp, data), key=itemgetter(0))]
