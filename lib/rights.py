import cherrypy
import lib.db_sql as db_sql

def check_rights():
    try:
        temp = cherrypy.request.path_info.split("/")[2]
    except IndexError:
        raise cherrypy.HTTPRedirect("/")
    view_user = db_sql.user_by_name(temp)
    if view_user == None:
        raise cherrypy.HTTPError(404, "Profile not found")
    elif view_user['privacy'] == 'private':
        user = cherrypy.session.get('username')
        if (user == view_user['username'] and
            cherrypy.session.id in view_user['session_ids']):
            return
        raise cherrypy.HTTPError(404, "Profile not public")

cherrypy.tools.rights = cherrypy.Tool('before_handler', check_rights)
