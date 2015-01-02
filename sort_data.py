import locale
locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
from natsort import index_humansorted, order_by_index

from variables import articles

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

        if row[field].split(maxsplit=1)[0].lower() in articles:
            temp[-1] = temp[-1] + row[field].split(maxsplit=1)[1] + row[field].split(maxsplit=1)[0]
        else:
           temp[-1] = temp[-1] + row[field]
    index = index_humansorted(temp)
    return order_by_index(data, index)
