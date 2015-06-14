# If you change something in this file you need to logout and login
# to change the db
def T_(message):
    """For translation with gettext"""
    return message
# You don't need the T_(…) aournd text
# if you don't plan to translate your template
TEMPLATES = {'book': {'name': T_('Book'),
                      'fields': [[{'text': T_('Author'),
                                   'field': 'authors'}]]},
             'comic': {'name': T_('Comic'),
                       'fields': [[{'text': T_('Author'),
                                    'field': 'authors'}],
                                  [{'text': T_('Artist'),
                                    'field': 'artist'}],
                                  [{'text': T_('Colorist'),
                                    'field': 'colorist'},
                                   {'text': T_('Cover Artist'),
                                    'field': 'cover_artist'}]]},
             'audiobook': {'name': T_('Audiobook'),
                           'fields': [[{'text': T_('Author'),
                                        'field': 'authors'}],
                                      [{'text': T_('Narrator'),
                                        'field': 'narrator'}]]}}

ORDER = ['book', 'comic', 'audiobook']
