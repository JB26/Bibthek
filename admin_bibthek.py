import argparse
from lib.mongo import mongo_role 

parser = argparse.ArgumentParser(description='BibThek')
parser.add_argument('--admin', type = str,
                    help = 'The user you want to make an admin',
                    metavar = "Username")
args = parser.parse_args()
if args.admin != None:
    print(mongo_role(args.admin, 'admin'))
