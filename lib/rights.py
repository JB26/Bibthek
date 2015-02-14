import cherrypy
from lib.mongo import mongo_user, mongo_user_rights

def check_rights():
    temp = cherrypy.request.path_info.split("/")[2]
    view_user = mongo_user_rights(temp)
    if view_user == None:
        raise cherrypy.HTTPError(404, "Profile not found")
    elif 'privacy' not in view_user or view_user['privacy'] == 'private':
        user = mongo_user(cherrypy.session.id)
        if user != None and user['username'] == view_user['username']:
          return
        raise cherrypy.HTTPRedirect("/")

cherrypy.tools.rights = cherrypy.Tool('before_handler', check_rights)
