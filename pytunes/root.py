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

class Root:
    """ Root class """
    def __init__(self):
        """ Do nothing on load """
        self.logger = logging.getLogger('pytunes.root')
        pass

    @cherrypy.expose(alias='robots.txt')
    def robots(self):
        if pytunes.settings.get('robots'):
            r = "User-agent: *\nDisallow: /\n"
        else:
            r = "User-agent: *\nDisallow: /logout/\nDisallow: /restart/\nDisallow: /shutdown/\nDisallow: /update/\nDisallow: /manager/\nDisallow: /settings/"
        return cherrypy.lib.static.serve_fileobj(r, content_type='text/plain', disposition=None, name='robots.txt', debug=False)   

    @cherrypy.expose()
    def index(self):
        """ Load template for frontpage """
        return pytunes.LOOKUP.get_template('dash.html').render(scriptname='dash')

    @cherrypy.expose()
    def default(self, *args, **kwargs):
        """ Show error if no matching page can be found """
        return "An error occured"

    @cherrypy.expose()
    def notices(self):
        """ Show notices """
        return "Notice"

    @cherrypy.expose()
    def shutdown(self):
        """ Shutdown CherryPy and exit script """
        self.logger.info("Shutting down PyTunes.")
        cherrypy.engine.exit()
        return "PyTunes Media Server Manager has shut down"

    @cherrypy.tools.json_out()
    @cherrypy.expose()
    def restart(self):
        """ Shutdown script and rerun with the same variables """
        self.logger.info("Restarting PyTunes.")
        Thread(target=do_restart).start()
        return "Restart in progress."

    @cherrypy.expose
    def logout(self, from_page="/"):
        sess = cherrypy.session
        username = sess.get(SESSION_KEY, None)
        sess[SESSION_KEY] = None
        if username:
            cherrypy.request.login = None
        raise cherrypy.HTTPRedirect(from_page or "/")

