def menu_data(mongo, shelf, _filter, sort_first, sort_second):
    sort1 = [
        {'name' : 'Title', 'url' : '/title/title/', 'active' : False},
        {'name' : 'Series', 'url' : '/series/variant1/', 'active' : False},
        {'name' : 'Author', 'url' : '/author/year/', 'active' : False},
        {'name' : 'Publisher', 'url' : '/publisher/year/', 'active' : False},
        {'name' : 'Genre', 'url' : '/genre/title/', 'active' : False}
        ]
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
            print('ok')
            items = mongo.titles(shelf, 'pages', _filter)
            sort2[2]['active'] = True
            active_sort = sort2[2]['url']
        print(sort_second)
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
    elif sort_first == 'author':
        sort1[2]['active'] = True
        sort2 = [{'name' : 'Year', 'url' : '/author/year/',
                  'active' : False},
                 {'name' : 'Title', 'url' : '/author/title/',
                  'active' : False}]
        if sort_second == 'year':
            items = mongo.authors(shelf, 'year', _filter)
            sort2[0]['active'] = True
            active_sort = sort2[0]['url']
        elif sort_second == 'title':
            items = mongo.authors(shelf, 'title', _filter)
            sort2[1]['active'] = True
            active_sort = sort2[1]['url']
    elif sort_first == 'publisher':
        sort1[3]['active'] = True
        sort2 = [{'name' : 'Title', 'url' : '/publisher/title/',
                  'active' : False},
                 {'name' : 'Year', 'url' : '/publisher/year/',
                  'active' : False}]
        if sort_second == 'title':
            items = mongo.publisher(shelf, 'title', _filter)
            sort2[0]['active'] = True
            active_sort = sort2[0]['url']
        elif sort_second == 'year':
            items = mongo.publisher(shelf, 'year', _filter)
            sort2[1]['active'] = True
            active_sort = sort2[1]['url']
    elif sort_first == 'genre':
        sort1[4]['active'] = True
        sort2 = [{'name' : 'Year', 'url' : '/genre/year/',
                  'active' : False},
                 {'name' : 'Title', 'url' : '/genre/title/',
                  'active' : False}]
        if sort_second == 'year':
            items = mongo.genre(shelf, 'year', _filter)
            sort2[0]['active'] = True
            active_sort = sort2[0]['url']
        elif sort_second == 'title':
            items = mongo.genre(shelf, 'title', _filter)
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
