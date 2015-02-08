def menu_data(mongo, shelf, _filter, sort_first, sort_second):
    sort1 = [
        {'name' : 'Title', 'url' : '/title/title/', 'active' : False},
        {'name' : 'Series', 'url' : '/series/variant1/', 'active' : False},
        {'name' : 'Author', 'url' : '/authors/year/', 'active' : False},
        {'name' : 'Publisher', 'url' : '/publisher/year/', 'active' : False},
        {'name' : 'Genre', 'url' : '/genre/title/', 'active' : False},
        {'name' : 'Artist', 'url' : '/artist/year/', 'active' : False},
        {'name' : 'Colorist', 'url' : '/colorist/year/', 'active' : False},
        {'name' : 'Cover artist', 'url' : '/cover_artist/year/',
         'active' : False},
        ]
    sort_similar = ['authors', 'publisher', 'genre', 'artist', 'colorist',
                    'cover_artist']
    if sort_first == 'title':
        sort1[0]['active'] = True
        sort2 = [{'name' : 'Year', 'url' : '/title/year/',
                  'active' : False},
                 {'name' : 'Title', 'url' : '/title/title/',
                  'active' : False},
                 {'name' : 'Pages', 'url' : '/title/pages/',
                  'active' : False}]
        if sort_second == 'year':
            items = mongo.titles(shelf, 'year', _filter)
            sort2[0]['active'] = True
            active_sort = sort2[0]['url']
        elif sort_second == 'title':
            items = mongo.titles(shelf, 'title', _filter)
            sort2[1]['active'] = True
            active_sort = sort2[1]['url']
        elif sort_second == 'pages':
            items = mongo.titles(shelf, 'pages', _filter)
            sort2[2]['active'] = True
            active_sort = sort2[2]['url']
    elif sort_first == 'series':
        sort1[1]['active'] = True
        sort2 = [{'name' : 'Variant 1',
                  'url' : '/series/variant1/', 'active' : False},
                 {'name' : 'Variant 2',
                  'url' : '/series/variant2/', 'active' : False}]
        if sort_second == 'variant1':
            items = mongo.series(shelf, 1, _filter)
            sort2[0]['active'] = True
            active_sort = sort2[0]['url']
        elif sort_second == 'variant2':
            items = mongo.series(shelf, 2, _filter)
            sort2[1]['active'] = True
            active_sort = sort2[1]['url']
    elif sort_first in sort_similar:
        sort1[sort_similar.index(sort_first) + 2]['active'] = True
        sort2 = [{'name' : 'Year', 'url' : '/' + sort_first + '/year/',
                  'active' : False},
                 {'name' : 'Title', 'url' : '/' + sort_first + '/title/',
                  'active' : False}]
        if sort_second == 'year':
            items = mongo.author_and_more(sort_first, shelf, 'year', _filter)
            sort2[0]['active'] = True
            active_sort = sort2[0]['url']
        elif sort_second == 'title':
            items = mongo.author_and_more(sort_first, shelf, 'title', _filter)
            sort2[1]['active'] = True
            active_sort = sort2[1]['url']

    return sort1, sort2, active_sort, items

def menu_filter(mongo, shelf):
    return [
        {
            'name' : 'Status', 'short' : 'stat_',
            'filter' : ['Unread', 'Read']
        },
        {
            'name' : 'Form', 'short' : 'form_',
            'filter' : ['Physical', 'Digital', 'Borrowed']
        },
        {
            'name' : 'Language', 'short' : 'lang_',
            'filter' : mongo.filter_list(shelf, 'language')
        },
        {
            'name' : 'Binding', 'short' : 'bind_',
            'filter' : mongo.filter_list(shelf, 'binding')
        }
        ]
