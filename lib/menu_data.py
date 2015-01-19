def menu_data(mongo, shelf, _filter, sort_first, sort_second):
    sort1 = [{'name' : 'Title', 'url' : '/title/title/',
              'active' : False},
             {'name' : 'Series', 'url' : '/series/variant1/',
              'active' : False},
             {'name' : 'Author', 'url' : '/author/year/',
              'active' : False}]
    if sort_first == 'title':
        items = mongo.titles(shelf, _filter)
        sort1[0]['active'] = True
        sort2 = [{'name' : 'Title', 'url' : '/title/title/',
                  'active' : True}]
        active_sort = sort2[0]['url']
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
        if sort_second == 'variant2':
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
    return sort1, sort2, active_sort, items
