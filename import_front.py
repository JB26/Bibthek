import os
import tarfile
from random import random
import hashlib

def untar(username):
    tar = tarfile.open('import/' + username + "_front.tar")
    for file_name in tar.getnames():
        if '/' in file_name:
            return 'No folders, please!', 1
        file_type = file_name.rsplit('.',1)
        if len(file_type) != 2:
            return "No fileextension?"
        if file_type[-1] not in  ['jpg', 'png', 'jpeg']:
            return "Only png and jpg", 1
    try:
        os.mkdir('import/' + username + '_pics')
    except:
        return "Last import went wrong", 1
    tar.extractall('import/' + username + '_pics')
    try:
        os.mkdir('static/' + username + '_front')
    except:
        pass
    return os.listdir('import/' + username + '_pics'), 0

def move(front, username, book_id):
    new_name = hashlib.sha224( bytes( str(random()) + str(book_id),
                                      'utf-8')).hexdigest()
    new_name = 'front/' + new_name + '.' + front.rsplit('.',1)[-1]
    os.rename('import/' + username + '_pics/' + front, 'html/' + new_name)
    return new_name

def del_pic(front, username):
    os.remove('import/' + username + '_pics/' + front)

def del_dir(username):
    try:
        os.rmdir('import/' + username + '_pics')
    except:
        return "forgotten covers"
    return "ok"
