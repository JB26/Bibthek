import sqlite3
from datetime import date

from import_cleaner import clean_import
from variables import dbnames, name_fields

def import_sqlite3(sql_file, separator):
    conn = sqlite3.connect(sql_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    data = []

    for row in c.execute('SELECT * FROM items'):
        row_dict = {}
        for fieldname in dbnames:
            if fieldname in row.keys():
                row_dict[fieldname] = row[fieldname]
                if fieldname in name_fields and separator != '&':
                   row_dict[fieldname] = row_dict[fieldname].replace(separator,
                                                                     " &")

        if ('isbn' in row_dict and
            row_dict['isbn'] != '') or ('author' in row_dict and
                                        row_dict['author'] != ''):
            row_dict = clean_import(row_dict)
            data.append(row_dict)
    return data
