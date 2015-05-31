"""Check the data fields for unexpected data"""
from lib.variables import VARIABLES
from lib.data_cleaner import date_clean

def sanity_check(params):
    """Check for unexpected data"""
    data = {}
    # Get rid of unexpected values and check for unexpected arrays
    for name in VARIABLES.fieldnames:
        if name in params:
            if isinstance(params[name], list) and name not in ('finish_date',
                                                               'start_date',
                                                               'abdoned',
                                                               'front'):
                return None, "No list allowed in " + name
            # Cherrypy forgets to decode long strings…
            elif isinstance(params[name], bytes) and (name not in
                                                      ('finish_date',
                                                       'start_date',
                                                       'abdoned',
                                                       'front')):
                params[name] = params[name].decode('utf-8')
            data[name] = params[name]
    if 'title' not in data or data['title'] == '':
        return None, "A book needs a title"
    # Check dates
    for name in VARIABLES.data_fields:
        if name in params:
            # ('finish_date', 'start_date') are allowed to be lists -> make all
            # other dates lists too.
            if not isinstance(data[name], list):
                date_temp = [data[name]]
            else:
                date_temp = data[name]
            for i in range(len(date_temp)):
                if date_temp[i] != '':
                    date_temp[i] = date_clean(date_temp[i])
                    if date_temp[i] == False:
                        return None, name + " is not a valid date"
            # Getting rid of unnecessary lists
            if name not in ['finish_date', 'start_date']:
                data[name] = date_temp[0]
            else:
                data[name] = date_temp
    return data, "0"
