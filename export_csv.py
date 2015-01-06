import csv
from variables import fieldnames

def export_csv(data, username):
    with open('export/books_' + username + '.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                            delimiter=';', quotechar='|',
                            quoting=csv.QUOTE_MINIMAL)

        writer.writeheader()
        for row in data:
            row['front'] = row['front'].rsplit('/',1)[-1]
            writer.writerow(row)
        return 'export/books_' + username + '.csv'
