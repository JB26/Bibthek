import csv
from datetime import date
import date_clean

from mongo_db import mongo_insert
from variables import fieldnames

with open('export.csv') as csvfile:
    csvimport = csv.DictReader(csvfile, fieldnames, delimiter=';')
    next(csvimport) #ignore first line
    for row in csvimport:
        row['authors'] = row['authors'].split(', ')
        row['genre'] = row['genre'].split(', ')
        print(row['release_date'])
        for dates in ['release_date', 'add_date']:
            row[dates] = date_clean.cleaner(row[dates])
        print(row['release_date'])
        mongo_insert(row)
