from app.app import bibthek
import argparse
import cherrypy
from app.db.mongo import mongo_role

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BibThek')
    parser.add_argument('--admin', type = str,
                        help = 'The user you want to make an admin',
                        metavar = "Username")
    args = parser.parse_args()
    if args.admin != None:
        print(mongo_role(args.admin, 'admin'))
    cherrypy.quickstart(bibthek(), '/', 'app.conf')
