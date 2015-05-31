"""Export a users book data"""
import zipfile
import csv
from lib.variables import VARIABLES

def export_csv(data, username):
    """Export a csv file"""
    with open('export/books_' + username + '.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=VARIABLES.dbnames,
                                delimiter=';', quotechar='|',
                                quoting=csv.QUOTE_MINIMAL)

        writer.writeheader()
        for row in data:
            if 'front' in row:
                row['front'] = 'covers/' + row['front'].rsplit('/', 1)[-1]
            #For development
            illegal_keys = []
            for key in row:
                if key not in VARIABLES.dbnames:
                    illegal_keys.append(key)
            for key in illegal_keys:
                del row[key]
            writer.writerow(row)
        return 'export/books_' + username + '.csv'

def export_cover_csv(data, username):
    """Export a zip with a csv and all covers"""
    file_list = []
    zip_name = "export/covers+csv_" + username + ".zip"
    zip_file = zipfile.ZipFile(zip_name, 'w')
    for row in data:
        if 'front' in row:
            file_list.append(row['front'])
    for _file in file_list:
        try:
            zip_file.write(_file, arcname='covers/' + _file.rsplit('/')[-1])
        except FileNotFoundError:
            pass
    csv_file = export_csv(data, username)
    zip_file.write(csv_file, arcname='export_' + username + '.csv')
    zip_file.close()
    return  zip_name
