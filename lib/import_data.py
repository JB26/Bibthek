"""Import users book data"""
import sqlite3
import csv
from shutil import rmtree
import os
import zipfile
from ast import literal_eval

from lib.data_cleaner import clean_import
from lib.variables import VARIABLES
from lib.book_data import cover_name

def import_file(data_uploaded, username, separator):
    """Import file and return data"""
    data_file = username + '_' + data_uploaded.filename
    data_file = 'import/' + data_file
    with open(data_file, 'wb') as _file:
        _file.write(data_uploaded.file.read())
    data, error = read_file(data_file, username, separator)
    os.remove(data_file)
    rmtree('import/' + username)
    return data, error

def read_file(data_file, username, separator):
    """Read data from file"""
    if data_file.rsplit('.', 1)[-1] == 'sqlite':
        data = import_sqlite3(data_file, separator)
    elif data_file.rsplit('.', 1)[-1] == 'csv':
        data = import_csv(data_file, separator)
    elif data_file.rsplit('.', 1)[-1] == 'zip':
        data_file, cover_list, error = unzip(data_file, username)
        if error != '0':
            return None, error
        if data_file.rsplit('.', 1)[-1] == 'sqlite':
            data = import_sqlite3(data_file, separator)
        elif data_file.rsplit('.', 1)[-1] == 'csv':
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
    """Try to format the imported data"""
    data_temp = {}
    for fieldname in VARIABLES.dbnames:
        if fieldname in _import.keys():
            data_temp[fieldname] = _import[fieldname]
            if fieldname in VARIABLES.name_fields and separator != '&':
                data_temp[fieldname] = data_temp[fieldname].replace(separator,
                                                                    " &")
            if fieldname == 'reading_stats':
                data_temp[fieldname] = literal_eval(data_temp[fieldname])
            if fieldname == 'form' and data_temp[fieldname] == 'Physical':
                data_temp[fieldname] = _import['binding']
    if 'title' in data_temp and data_temp['title'] != '':
        data_temp = clean_import(data_temp)
        return data_temp
    else:
        return None

def import_csv(csv_file, separator):
    """Read csv file"""
    data = []
    with open(csv_file) as csvfile:
        csvimport = csv.DictReader(csvfile, delimiter=';', quotechar='|')
        for row in csvimport:
            row = import_data(row, separator)
            if row != None:
                data.append(row)
    return data

def import_sqlite3(sql_file, separator):
    """Read sqlite db"""
    conn = sqlite3.connect(sql_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    data = []
    for row in cursor.execute('SELECT * FROM items'):
        row = import_data(row, separator)
        if row != None:
            data.append(row)
    return data

def unzip(data_zip, username):
    """Unzip and check upload"""
    zip_file = zipfile.ZipFile(data_zip, 'r')
    data_found = False
    for file_name in zip_file.namelist():
        if file_name != 'covers/':
            fns = file_name.split('/')
            if len(fns) > 2 or (fns[0] != 'covers' and len(fns) == 2):
                return None, None, 'No other folders than "covers/", please!'
            file_type = file_name.rsplit('.', 1)
            if len(file_type) != 2:
                return None, None, "No fileextension?"
            if fns[0] == 'covers':
                if file_type[-1] not in  ['jpg', 'png', 'jpeg']:
                    return None, None, "Only png and jpg"
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
    zip_file.extractall('import/' + username)
    data_file = ('import/' + username + '/' + data_file)
    try:
        os.mkdir('static/covers/' + username + '_front')
    except FileExistsError:
        pass
    return data_file, os.listdir('import/' + username + '/covers'), '0'

def move_cover(front, username):
    """Move imported covers"""
    file_type = front.rsplit('.', 1)[-1]
    new_name, error = cover_name(username, file_type)
    os.rename('import/' + username + '/covers/' + front, new_name)
    return new_name, error
