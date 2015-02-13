import cherrypy
from lib.mongo import mongo_user, mongo_user_rights

def check_rights():
    view_user = cherrypy.request.path_info.split("/")[2]
    user = mongo_user_rights(view_user)
    if user == None:
        raise cherrypy.HTTPError(404, "Profile not found")
    elif ( ( 'privacy' not in user or user['privacy'] == 'private' ) and
           ( view_user != cherrypy.session['username'] ) ):
        raise cherrypy.HTTPRedirect("/")
    
cherrypy.tools.rights = cherrypy.Tool('before_handler', check_rights)
