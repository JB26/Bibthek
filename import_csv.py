import csv
from datetime import date

from import_cleaner import clean_import
from variables import dbnames, name_fields

def import_csv(csv_file, separator):
    data = []
    
    with open(csv_file) as csvfile:
        csvimport = csv.DictReader(csvfile, delimiter=';', quotechar='|')
        for row in csvimport:
            row_dict = {}
            for fieldname in dbnames:
                if fieldname in row:
                    row_dict[fieldname] = row[fieldname]
                    if fieldname in name_fields and separator != '&':
                        row_dict[fieldname] = row_dict[fieldname].replace(separator," &")
            if ('isbn' in row_dict and
            row_dict['isbn'] != '') or ('author' in row_dict and
                                        row_dict['author'] != ''):
                row_dict = clean_import(row_dict)
                data.append(row_dict)
    return data
