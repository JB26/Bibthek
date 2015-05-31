import cherrypy
from lib.db_users import user_by_name

def check_auth(required = True, user_role = None):
    if required:
        if cherrypy.session.get('username') != None:
            user = user_by_name(cherrypy.session.get('username'))
            if user == None or cherrypy.session.id not in user['session_ids']:
                cherrypy.lib.sessions.expire()
                raise cherrypy.HTTPRedirect("/login")
            elif user_role != None and user['role'] != user_role:
                raise cherrypy.HTTPRedirect("/login")
        else:
            raise cherrypy.HTTPRedirect("/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)
