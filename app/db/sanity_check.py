from app.variables import fieldnames, date_fields
from app.db.data_cleaner import date_clean

def sanity_check(params):
    data = {}
    # Get rid of unexpected values and check for unexpected arrays
    for name in fieldnames:
        if name in params:
            if type(params[name]) is list and name not in ('finish_date',
                                                           'start_date',
                                                           'abdoned',
                                                           'front'):
                raise Exception("No list allowed in " + name)
            # Cherrypy forgets to decode long strings… 
            elif type(params[name]) is bytes and name not in ('finish_date',
                                                              'start_date',
                                                              'abdoned',
                                                              'front'):
                params[name] = params[name].decode('utf-8')
                
            data[name] = params[name]
    if 'title' not in data:
        raise Exception("A book needs a title")
    # Check dates
    for name in date_fields:
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
                        raise Exception(name + " is not a valid date")
            # Getting rid of unnecessary lists
            if len(date_temp) == 1:
                data[name] = date_temp[0]
            else:
                data[name] = date_temp
    return data
            
