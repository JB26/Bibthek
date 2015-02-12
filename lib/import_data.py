import sqlite3
import csv
from datetime import date
from shutil import rmtree
import os
import zipfile
from random import random
import hashlib
from ast import literal_eval

from lib.data_cleaner import clean_import
from lib.variables import dbnames, name_fields
from lib.book_data import cover_name

def import_file(data_uploaded, username, separator):
    data_file = username + '_' + data_uploaded.filename
    data_file = 'import/' + data_file
    with open(data_file , 'wb') as f:
        f.write(data_uploaded.file.read())
    data, error = read_file(data_file, username, separator)
    os.remove(data_file)
    rmtree('import/' + username)
    return data, error
    
def read_file(data_file, username, separator):
    if data_file.rsplit('.',1)[-1] == 'sqlite':
        data = import_sqlite3(new_name, separator)
    elif data_file.rsplit('.',1)[-1] == 'csv':
        data = import_csv(new_name, separator)
    elif data_file.rsplit('.',1)[-1] == 'zip':
        data_file, cover_list, error = unzip(data_file, username)
        if error != '0':
            return None, error
        if data_file.rsplit('.',1)[-1] == 'sqlite':
            data = import_sqlite3(data_file, separator)
        elif data_file.rsplit('.',1)[-1] == 'csv':
            data = import_csv(data_file, separator)
        else:
            return None, "No csv or sqlite found"
        for book in data:
            if book['front'][7:] in cover_list:
                new_name, error = move_cover(book['front'][7:], username)
                if error != '0':
                    return None, error
                book['front'] = new_name
    else:
        return None, "Only csv, sqlite or zip"
    return data, '0'

def import_data(_import, separator):
    data_temp = {}
    for fieldname in dbnames:
        if fieldname in _import.keys():
            data_temp[fieldname] = _import[fieldname]
            if fieldname in name_fields and separator != '&':
                data_temp[fieldname] = data_temp[fieldname].replace(separator,
                                                                " &")
            if fieldname == 'reading_stats':
                data_temp[fieldname] = literal_eval(data_temp[fieldname])
    if ('isbn' in data_temp and
        data_temp['isbn'] != '') or ('author' in data_temp and
                                    data_temp['author'] != ''):
        data_temp = clean_import(data_temp)
        return data_temp
    else:
        return None

def import_csv(csv_file, separator):
    data = []
    with open(csv_file) as csvfile:
        csvimport = csv.DictReader(csvfile, delimiter=';', quotechar='|')
        for row in csvimport:
            row = import_data(row, separator)
            if row != None:
                data.append(row)
    return data

def import_sqlite3(sql_file, separator):
    conn = sqlite3.connect(sql_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    data = []
    for row in c.execute('SELECT * FROM items'):
        row = import_data(row, separator)
        if row != None:
            data.append(row)
    return data

def unzip(data_zip, username):
    zf = zipfile.ZipFile(data_zip, 'r')
    data_found = False
    for file_name in zf.namelist():
        if file_name != 'covers/':
            fns = file_name.split('/')
            if len(fns) > 2 or (fns[0] != 'covers' and len(fns) == 2):
                return None, None, 'No other folders than "covers/", please!'
            file_type = file_name.rsplit('.',1)
            if len(file_type) != 2:
                return None, None, "No fileextension?"
            if fns[0] == 'covers':
                if file_type[-1] not in  ['jpg', 'png', 'jpeg']:
                    return None, None, "Only png and jpg", 1
            elif file_type[-1] in ['csv', 'sqlite']:
                if data_found:
                    return None, None, "Only one data file allowed"
                data_file = file_name
                data_found = True
            else:
                return None, None, "Only csv and sqlite supported"
            
    try:
        os.mkdir('import/' + username)
    except FileExistsError:
        return None, None, "Last import went wrong"
    zf.extractall('import/' + username )
    data_file = ('import/' + username + '/' + data_file)
    try:
        os.mkdir('static/covers/' + username + '_front')
    except FileExistsError:
        pass
    return data_file, os.listdir('import/' + username + '/covers'), '0'

def move_cover(front, username):
    file_type = front.rsplit('.',1)[-1]
    new_name, error = cover_name(username, file_type)
    os.rename('import/' + username + '/covers/' + front, new_name)
    return new_name, error
