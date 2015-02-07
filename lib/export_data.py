import zipfile
import csv
from lib.variables import dbnames

def export_csv(data, username):
    with open('export/books_' + username + '.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=dbnames,
                            delimiter=';', quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)

        writer.writeheader()
        for row in data:
            if 'front' in row:
                row['front'] = 'covers/' + row['front'].rsplit('/',1)[-1]
            #For development
            illegal_keys = []
            for key in row:
                if key not in dbnames:
                    illegal_keys.append(key)
            for key in illegal_keys:
                del row[key]
            writer.writerow(row)
        return 'export/books_' + username + '.csv'

def export_cover_csv(data, username):
    file_list = []
    zip_name = "export/covers+csv_" + username + ".zip"
    zf = zipfile.ZipFile(zip_name, 'w')
    for row in data:
        if 'front' in row:
            file_list.append(row['front'])
    for _file in file_list:
        try:
            zf.write(_file,
                     arcname='covers/' + _file.rsplit('/')[-1])
        except:
            pass
    csv_file = export_csv(data, username)
    zf.write(csv_file, arcname='export_' + username + '.csv')
    zf.close()
    return  zip_name
