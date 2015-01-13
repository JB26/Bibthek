from datetime import date
from variables import articles
from datetime import date

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def clean_import(row):
    if 'isbn' in row : row['isbn'] = row['isbn'].replace("-","")
    row['title'] = title_clean(row['title'])
    row['order'], row['title'] = number_clean(row['title'])
    for _date in ['release_date', 'add_date', 'start_date', 'finish_date']:
        if _date in row :
            if row[_date] != '':
                date_temp = date_clean(row[_date])
                if date_temp != False:
                    row[_date] = date_clean(row[_date])
                else:
                     row[_date] = ''
    if 'add_date' not in row or row['add_date'] == '' :
        row['add_date'] = str(datetime.date())
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
            except:
                row['read_count'] = 0
            row['reading_stats'] = [{"start_date":'',
                                     "finish_date":''}] * row['read_count']
    return row

def title_clean(title):
    title_temp = title.rsplit(maxsplit=1)
    if len(title_temp) == 2 and title_temp[1][1:-1].lower() in articles and title_temp[1][0] == "(" and title_temp[1][-1] == ")":
        return title_temp[1][1:-1] + ' ' + title_temp[0]
    else:
        return title

def number_clean(title):
    title_temp = title.split(maxsplit=2)
    if len(title_temp) == 3 and is_int(title_temp[0]) and title_temp[1] ==  '-':
        return title_temp[0], title_temp[2]
    else:
        return '', title
    

def date_clean(date):
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
            date_temp[0], date_temp[1],  date_temp[2] = date_temp[2], date_temp[0], date_temp[1]
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
