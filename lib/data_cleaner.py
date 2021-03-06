"""Clean up and prepare imported and saved books for storing in the db"""
from datetime import datetime
from lib.variables import VARIABLES

def is_int(string):
    """Check if a string is an int"""
    try:
        int(string)
        return True
    except ValueError:
        return False

def clean_import(row):
    """Clean up data"""
    if 'isbn' in row:
        row['isbn'] = row['isbn'].replace("-", "")
    row['title'] = title_clean(row['title'])
    if 'order_nr' not in row or row['order_nr'] == '':
        row['order_nr'], row['title'] = number_clean(row['title'])
    for _date in ['release_date', 'add_date', 'start_date', 'finish_date']:
        if _date in row:
            if row[_date] != '':
                date_temp = date_clean(row[_date])
                if date_temp != False:
                    row[_date] = date_clean(row[_date])
                else:
                    row[_date] = ''
    if 'add_date' not in row or row['add_date'] == '':
        row['add_date'] = str(datetime.now()[:10])
    if 'series_complete' in row:
        if row['series_complete'] == 'True':
            row['series_complete'] = True
        elif row['series_complete'] == 'False':
            row['series_complete'] = False
    if 'series' in row and row['series'][-4:] == ' (*)':
        row['series'] = row['series'][0:-4]
        row['series_complete'] = True
    if 'read_count' in row and row['read_count'] != '':
        if 'reading_stats' not in row or row['reading_stats'] == '':
            try:
                row['read_count'] = int(row['read_count'])
            except ValueError:
                row['read_count'] = 0
            row['reading_stats'] = [{"start_date":'',
                                     "finish_date":''}] * row['read_count']
    return row

def title_clean(title):
    """Clean title"""
    title_temp = title.rsplit(maxsplit=1)
    if (len(title_temp) == 2 and
            title_temp[1][1:-1].lower() in VARIABLES.articles and
            title_temp[1][0] == "(" and title_temp[1][-1] == ")"):
        return title_temp[1][1:-1] + ' ' + title_temp[0]
    else:
        return title

def number_clean(title):
    """Try to guess series number"""
    title_temp = title.split(' - ', maxsplit=1)
    if (len(title_temp) == 2 and is_int(title_temp[0]) and
            len(title_temp[0]) < 3):
        return title_temp[0], title_temp[1]
    else:
        return '', title

def date_clean(date):
    """Try to convert different date formats"""
    if "." in date:
        date_temp = date.split('.')
        if len(date_temp) == 2:
            date_temp[0], date_temp[1] = date_temp[1], date_temp[0]
        elif len(date_temp) == 3:
            date_temp[0], date_temp[2] = date_temp[2], date_temp[0]
        else:
            return False
    elif "-" in date:
        date_temp = date.split('-')
        if len(date_temp) > 3:
            return False
    elif "/" in date:
        date_temp = date.split('/')
        if len(date_temp) == 2:
            date_temp[0], date_temp[1] = date_temp[1], date_temp[0]
        elif len(date_temp) == 3:
            date_temp[0], date_temp[1], date_temp[2] = (date_temp[2],
                                                        date_temp[0],
                                                        date_temp[1])
        else:
            return False
    else:
        date_temp = [date]
    for value in date_temp:
        if is_int(value) == False:
            return False
    if len(date_temp[0]) == 2:
        now = date.today()
        if int(date_temp[0]) <= now.year + 3:
            date_temp[0] = "20" + date_temp[0]
        else:
            date_temp[0] = "19" + date_temp[0]
    elif len(date_temp[0]) > 4:
        return False
    date = date_temp[0]
    for val in date_temp[1:]:
        if len(val) > 2:
            return False
        date = date + '-' + val
    return date
