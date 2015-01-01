import sqlite3
from datetime import date
from import_cleaner import clean_import

from mongo_db import mongo_insert
from variables import fieldnames

conn = sqlite3.connect('books.sqlite')
c = conn.cursor()

for row in c.execute('SELECT * FROM items'):
    row = {fieldnames[i]: row[i] for i in range(len(fieldnames))}

    row = clean_import(row)
    
    mongo_insert(row)
