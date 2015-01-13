import zipfile

def make_zip(username, mode):
    zip_name = "export/covers+csv_" + username + ".zip"
    zf = zipfile.ZipFile(zip_name, mode=mode)
    return zip_name, zf

def export_cover(data, username):
    file_list = []
    zip_name, zf = make_zip(username, 'w')
    for row in data:
        print(row)
        if 'front' in row:
            file_list.append(row['front'])
    for _file in file_list:
        try:
            zf.write('static/' + _file, arcname='covers/' + _file.rsplit('/')[-1])
        except:
            pass
    zf.close()
    return  zip_name

def append_csv (csv_file, username):
    zip_name, zf = make_zip(username, 'a')
    zf.write(csv_file, arcname='export_' + username + '.csv')
    zf.close()
    return  zip_name
