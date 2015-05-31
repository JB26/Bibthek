"""Give an user admin rights through the commandline"""
import argparse
import lib.db_users as db_users

def give_admin_rights():
    """Give an user admin rights"""
    parser = argparse.ArgumentParser(description='BibThek')
    parser.add_argument('--admin', type=str,
                        help='The user you want to make an admin',
                        metavar="Username")
    args = parser.parse_args()
    if args.admin != None:
        db_users.chg_role(args.admin, 'admin')

if __name__ == '__main__':
    give_admin_rights()
