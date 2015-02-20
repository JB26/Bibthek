import cherrypy
from lib.mongo import mongo_user_by_session

def check_auth(required = True, user_role = None):
    user = mongo_user_by_session(cherrypy.session.id)

    if required:
        if user == None:
            raise cherrypy.HTTPRedirect("/login")
        elif user_role != None and user['role'] != user_role:
            raise cherrypy.HTTPRedirect("/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)
