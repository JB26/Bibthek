import csv
from app.variables import dbnames

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
