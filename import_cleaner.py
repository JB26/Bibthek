from datetime import date
from variables import articles

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def clean_import(row):
    row['authors'] = row['authors'].split(', ')
    row['genre'] = row['genre'].split(', ')
    row['title'] = title_clean(row['title'])
    row['order'], row['title'] = number_clean(row['title'])
    for dates in ['release_date', 'add_date']:
        row[dates] = date_clean(row[dates])
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
            date_temp.insert(0,"00")
        date_temp[0], date_temp[2] = date_temp[2], date_temp[0]
    elif "-" in date:
        date_temp = date.split('-')
        if len(date_temp) == 2:
            date_temp.append("00")
    elif "/" in date:
        date_temp = date.split('/')
        if len(date_temp) == 2:
            date_temp.insert(1,"00")
        date_temp[0], date_temp[1],  date_temp[2] = date_temp[2], date_temp[0], date_temp[1]
    else:
        if date != '':
            date_temp = [date , "00", "00"]
        else:
            date_temp = ["0000", "00", "00"]
    for i in range(3):
        if is_int(date_temp[i]) == False:
            if i == 0:
                date_temp[i] = "0000"
            else:
                date_temp[i] = "00"
    if len(date_temp[0]) == 2:
        now = date.today()
        if int(date_temp[0]) <= now.year + 3:
            date_temp[0] = "20" + date_temp[0]
        else:
            date_temp[0] = "19" + date_temp[0]
    date = date_temp[0] + '-' +  date_temp[1] + '-' +  date_temp[2]
    return date
