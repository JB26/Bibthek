"""Authentication process"""
import cherrypy
import lib.db_users as db_users

def check_auth(required=True, user_role=None):
    """Check authentication"""
    if required:
        if cherrypy.session.get('username') != None:
            user = db_users.user_by_name(cherrypy.session.get('username'))
            if user == None or cherrypy.session.id not in user['session_ids']:
                cherrypy.lib.sessions.expire()
                raise cherrypy.HTTPRedirect("/login")
            elif user_role != None and user['role'] != user_role:
                raise cherrypy.HTTPRedirect("/login")
        else:
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
        user = cherrypy.session.get('username')
        if (user == view_user['username'] and
                cherrypy.session.id in view_user['session_ids']):
            return
        raise cherrypy.HTTPError(404, "Profile not public")
