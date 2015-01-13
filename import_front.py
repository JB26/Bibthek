import os
import zipfile
from random import random
import hashlib

def unzip(new_name, username):
    zf = zipfile.ZipFile(new_name, 'r')
    data_found = False
    for file_name in zf.namelist():
        fns = file_name.split('/', maxsplit=1)
        if len(fns) == 2 and fns[0] != 'covers':
            return None, 'No other folders than "covers/", please!', 1
        file_type = file_name.rsplit('.',1)
        if len(file_type) != 2:
            return None, "No fileextension?"
        if file_type[-1] not in  ['jpg', 'png', 'jpeg', 'csv', 'sqlite']:
            return None, "Only png and jpg", 1
        if file_type[-1] in ['csv', 'sqlite']:
            if data_found:
                return None, "Only one data file allowed", 1
            data_file = file_name
            data_found = True
            
    try:
        os.mkdir('import/' + username)
    except:
        return None, "Last import went wrong", 1
    zf.extractall('import/' + username )
    data_file = ('import/' + username + '/' + data_file)
    try:
        os.mkdir('static/covers/' + username + '_front')
    except:
        pass
    return data_file, os.listdir('import/' + username + '/covers'), 0

def move(front, username, book_id):
    new_name = hashlib.sha224( bytes( str(random()) + str(book_id),
                                      'utf-8')).hexdigest()
    new_name = 'static/covers/' + username + '_front/' + new_name
    new_name = new_name +  '.' + front.rsplit('.',1)[-1]
    os.rename('import/' + username + '/covers/' + front, new_name)
    print(new_name)
    return new_name

def del_pic(front, username):
    os.remove('import/' + username + '/covers/' + front)

def del_dir(data_file, username):
    try:
        os.rmdir('import/' + username + '/covers')
    except:
        return "forgotten covers"
    os.remove(data_file)
    os.rmdir('import/' + username)
    return "ok"
