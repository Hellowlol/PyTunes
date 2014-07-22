#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Root for webserver. Specifies frontpage, errorpage (default),
and pages for restarting and shutting down server.
"""
import os
import sys
import cherrypy
import pytunes
import logging
from threading import Thread
from cherrypy.lib.auth2 import *


def do_restart():
    arguments = sys.argv[:]
    arguments.insert(0, sys.executable)
    if '--nobrowser' not in arguments:
        arguments.append('--nobrowser')
    if sys.platform == 'win32':
        arguments = ['"%s"' % arg for arg in arguments]
    os.chdir(os.getcwd())
    cherrypy.engine.exit()
    os.execv(sys.executable, arguments)

class RestrictedArea:
    # all methods in this controller (and subcontrollers) is
    # open only to members of the admin group
    _cp_config = {
        'auth.require': [member_of('admin')]
    }
    

class Root:
    """ Root class """
    def __init__(self):
        """ Do nothing on load """
        self.logger = logging.getLogger('pytunes.root')
        pass
  
    auth = AuthController()
    restricted = RestrictedArea()
    
    @cherrypy.expose()
    @require()
    def index(self):
        """ Load template for frontpage """
        return pytunes.LOOKUP.get_template('dash.html').render(scriptname='dash')

    @cherrypy.expose()
    @require()
    def default(self, *args, **kwargs):
        """ Show error if no matching page can be found """
        return "An error occured"

    @cherrypy.expose()
    @require()
    def notices(self):
        """ Show notices """
        return "Notice"

    @cherrypy.expose()
    @require()
    def shutdown(self):
        """ Shutdown CherryPy and exit script """
        self.logger.info("Shutting down PyTunes.")
        cherrypy.engine.exit()
        return "PyTunes Media Server Manager has shut down"

    @cherrypy.tools.json_out()
    @cherrypy.expose()
    @require()
    def restart(self):
        """ Shutdown script and rerun with the same variables """
        self.logger.info("Restarting PyTunes.")
        Thread(target=do_restart).start()
        return "Restart in progress."

    @cherrypy.expose
    @require()
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
        raise cherrypy.HTTPRedirect(from_page or "/")