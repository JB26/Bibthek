import cherrypy
from mongo_db import mongo_user

def check_auth(required = True):
    if required:
        user = mongo_user(cherrypy.session.id)
        if user == None:
            raise cherrypy.HTTPRedirect("/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)
