import locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
from natsort import index_humansorted, order_by_index

from variables import articles

def sorted_shelfs(data):
    return library_sorted(data, '_id', False)

def sorted_author(data):
    temp = []
    for row in data:
        find_surname = row['_id'].rsplit(maxsplit=1)
        if len(find_surname) == 2:
            temp.append(find_surname[1] + ' ' + find_surname[0])
        elif len(find_surname) == 1:
            temp.append(row['_id'])
    index = index_humansorted(temp)
    return order_by_index(data, index)

def sorted_titles(data):
    return library_sorted(data, '_id', False)

def sorted_series(data):
    data = library_sorted(data, '_id', False)  #Sort series titles
    for i in range(len(data)):  #Sort book titles in series
        if 'series_hash' in data[i] : data[i]['books'] = library_sorted(data[i]['books'], 'title', True)
    return data
    

def library_sorted(data, field, sort_by_order):
    temp = []

    for row in data:
        if sort_by_order and 'order' in row:
            temp.append( str(row['order']) )
        else:
            temp.append('')
            find_article = row[field].split(maxsplit=1)
            if len(find_article) == 2 and find_article[0].lower() in articles:
                temp[-1] = temp[-1] + find_article[1] + find_article[0]
        temp[-1] = temp[-1] + row[field]
    index = index_humansorted(temp)
    return order_by_index(data, index)
