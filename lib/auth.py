"""Authentication process"""
import cherrypy
import lib.db_users as db_users

def check_auth(required=True, user_role=None):
    """Check authentication"""
    if required:
        user = db_users.user_by_session(cherrypy.session.id)
        if user == None:
            cherrypy.lib.sessions.expire()
            raise cherrypy.HTTPRedirect("/login")
        elif user_role != None and user['role'] != user_role:
            raise cherrypy.HTTPRedirect("/login")

def check_rights():
    """Check if the user has the right to visit a page"""
    try:
        temp = cherrypy.request.path_info.split("/")[2]
    except IndexError:
        raise cherrypy.HTTPRedirect("/")
    view_user = db_users.user_by_name(temp)
    if view_user == None:
        raise cherrypy.HTTPError(404, "Profile not found")
    elif view_user['privacy'] == 'private':
        user = db_users.user_by_session(cherrypy.session.id)
        if user == None or user['username'] != view_user['username']:
            raise cherrypy.HTTPError(404, "Profile not public")
