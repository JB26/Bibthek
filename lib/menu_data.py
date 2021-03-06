"""Return data needed to build the main menu"""
import lib.db_books as db_books

def T_(message):
    """For translation with gettext"""
    return message

def menu_data(username, active_filters, sort_first, sort_second):
    """Build the sort by menu and the sidebar"""
    sort1 = [
        {'name' : T_('Title'), 'url' : '/title/title/', 'active' : False},
        {'name' : T_('Series'), 'url' : '/series/variant1_order/',
         'active' : False},
        {'name' : T_('Author'), 'url' : '/authors/year/', 'active' : False},
        {'name' : T_('Publisher'), 'url' : '/publisher/year/', 'active' : False},
        {'name' : T_('Genre'), 'url' : '/genre/title/', 'active' : False},
        {'name' : T_('Narrator'), 'url' : '/narrator/year/', 'active' : False},
        {'name' : T_('Artist'), 'url' : '/artist/year/', 'active' : False},
        {'name' : T_('Colorist'), 'url' : '/colorist/year/', 'active' : False},
        {'name' : T_('Cover Artist'), 'url' : '/cover_artist/year/',
         'active' : False},
        ]
    sort_similar = ['authors', 'publisher', 'genre', 'narrator', 'artist',
                    'colorist', 'cover_artist']
    if sort_first == 'title':
        sort1[0]['active'] = True
        sort2 = [{'name' : T_('Year'), 'url' : '/title/year/',
                  'active' : False},
                 {'name' : T_('Title'), 'url' : '/title/title/',
                  'active' : False},
                 {'name' : T_('Pages'), 'url' : '/title/pages/',
                  'active' : False},
                 {'name' : T_('Date added'), 'url' : '/title/added/',
                  'active' : False}]
        if sort_second == 'year':
            items = db_books.titles(username, 'year', active_filters)
            sort2[0]['active'] = True
            active_sort = sort2[0]['url']
        elif sort_second == 'title':
            items = db_books.titles(username, 'title', active_filters)
            sort2[1]['active'] = True
            active_sort = sort2[1]['url']
        elif sort_second == 'pages':
            items = db_books.titles(username, 'pages', active_filters)
            sort2[2]['active'] = True
            active_sort = sort2[2]['url']
        elif sort_second == 'added':
            items = db_books.titles(username, 'added', active_filters)
            sort2[3]['active'] = True
            active_sort = sort2[3]['url']
    elif sort_first == 'series':
        sort1[1]['active'] = True
        sort2 = [{'name' : T_('Variant 1: Order'),
                  'url' : '/series/variant1_order/', 'active' : False},
                 {'name' : T_('Variant 1: Year'),
                  'url' : '/series/variant1_year/', 'active' : False},
                 {'name' : T_('Variant 2: Order'),
                  'url' : '/series/variant2_order/', 'active' : False},
                 {'name' : T_('Variant 2: Year'),
                  'url' : '/series/variant2_year/', 'active' : False}]
        sort2_series = ['variant1_order', 'variant1_year',
                        'variant2_order', 'variant2_year']
        if sort_second in sort2_series:
            items = db_books.series(username, sort_second,
                                    active_filters)
            i = sort2_series.index(sort_second)
            sort2[i]['active'] = True
            active_sort = sort2[i]['url']
    elif sort_first in sort_similar:
        sort1[sort_similar.index(sort_first) + 2]['active'] = True
        sort2 = [{'name' : T_('Year'), 'url' : '/' + sort_first + '/year/',
                  'active' : False},
                 {'name' : T_('Title'), 'url' : '/' + sort_first + '/title/',
                  'active' : False}]
        if sort_second == 'year':
            items = db_books.author_and_more(username, sort_first,
                                             'year', active_filters)
            sort2[0]['active'] = True
            active_sort = sort2[0]['url']
        elif sort_second == 'title':
            items = db_books.author_and_more(username, sort_first,
                                             'title', active_filters)
            sort2[1]['active'] = True
            active_sort = sort2[1]['url']

    return sort1, sort2, active_sort, items

def menu_filter(username, active_filters):
    """Build the filter menu"""
    return [
        {
            'name' : T_('Status'), 'short' : 'stat_',
            'filter' : db_books.filter_list_stat(username, active_filters)
        },
        {
            'name' : T_('Format'), 'short' : 'form_',
            'filter' : db_books.filter_list(username, 'form', active_filters)
        },
        {
            'name' : T_('Language'), 'short' : 'lang_',
            'filter' : db_books.filter_list(username, 'language',
                                            active_filters)
        },
        {
            'name' : T_('Shelf'), 'short' : 'shelf_',
            'filter' : db_books.filter_list(username, 'shelf', active_filters)
        }
        ]
