import cherrypy
from lib.mongo import mongo_user

def check_auth(required = True, user_role = None):
    if required:
        user = mongo_user(cherrypy.session.id)
        if user == None or (user_role != None and user['role'] != user_role):
            raise cherrypy.HTTPRedirect("/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)
