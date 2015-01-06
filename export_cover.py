import tarfile

def export_cover(data, username):
    file_list = []
    for row in data:
        file_list.append(row['front'])
    tar_name = "export/covers_" + username + ".tar"
    tar = tarfile.open(tar_name, "w")
    for _file in file_list:
        try:
            tar.add('html/' + _file, arcname=_file.rsplit('/')[-1])
        except:
            pass
    tar.close()
    return  tar_name
