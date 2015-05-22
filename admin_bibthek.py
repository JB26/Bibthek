import argparse
import lib.db_sql as db_sql 

parser = argparse.ArgumentParser(description='BibThek')
parser.add_argument('--admin', type = str,
                    help = 'The user you want to make an admin',
                    metavar = "Username")
args = parser.parse_args()
if args.admin != None:
    db_sql.role(args.admin, 'admin')
