#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
from urllib import quote
from urllib2 import urlopen, Request
from json import loads
import logging
import base64
from cherrypy.lib.auth2 import require


class NZBGet:
    def __init__(self):
        self.logger = logging.getLogger('modules.nzbget')
        pytunes.MODULES.append({
            'name': 'NZBGet',
            'id': 'nzbget',
            'test': '%snzbget/version' % pytunes.WEBDIR,
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'nzbget_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'nzbget_name'},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'nzbget_host'},
                {'type': 'text', 'label': 'Port *', 'name': 'nzbget_port'},
                {'type': 'text', 'label': 'Basepath', 'name': 'nzbget_basepath'},
                {'type': 'text', 'label': 'User', 'name': 'nzbget_username'},
                {'type': 'text', 'label': 'Password', 'name': 'nzbget_password'},
                {'type': 'bool', 'label': 'Use SSL', 'name': 'nzbget_ssl'}
        ]})

    @cherrypy.expose()
    @require()
    def index(self):
        return pytunes.LOOKUP.get_template('nzbget.html').render(scriptname='nzbget')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def version(self, nzbget_host, nzbget_basepath, nzbget_port, nzbget_username, nzbget_password, nzbget_ssl=False, **kwargs):
        self.logger.debug("Fetching version information from nzbget")
        ssl = 's' if nzbget_ssl else ''

        if(nzbget_basepath == ""):
            nzbget_basepath = "/"
        if not(nzbget_basepath.endswith('/')):
            nzbget_basepath += "/"

        url = 'http%s://%s:%s@%s:%s%sjsonrpc/' % (ssl, nzbget_username, nzbget_password, nzbget_host, nzbget_port, nzbget_basepath)
        try:
            return loads(urlopen('%sversion' % url, timeout=10).read())
        except:
            self.logger.error("Unable to contact nzbget via %s" % url)
            return

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetHistory(self, limit=''):
        self.logger.debug("Fetching history")
        return self.fetch('history')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetWarnings(self):
        self.logger.debug("Fetching warnings")
        return self.fetch('log?NumberOfEntries=1000&IDFrom=0')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetStatus(self):
        self.logger.debug("Fetching queue")
        return self.fetch('listgroups')
    
    def fetch(self, path):
        try:
            host = pytunes.settings.get('nzbget_host', '')
            port = str(pytunes.settings.get('nzbget_port', ''))
            username = pytunes.settings.get('nzbget_username', '')
            password = pytunes.settings.get('nzbget_password', '')
            nzbget_basepath = pytunes.settings.get('nzbget_basepath', '/')
            ssl = 's' if pytunes.settings.get('nzbget_ssl', True) else ''

            if(nzbget_basepath == ""):
                nzbget_basepath = "/"
            if not(nzbget_basepath.endswith('/')):
                nzbget_basepath += "/"
            
            url = 'http%s://%s:%s%sjsonrpc/%s' % (ssl, host, port, nzbget_basepath, path)
            request = Request(url)
            base64string = base64.encodestring('%s:%s' % (username, password).replace('\n', ''))
            request.add_header("Authorization", "Basic %s" % base64string) 
            self.logger.debug("Fetching information from: %s" % url)
            return loads(urlopen(request, timeout=10).read())
        except:
            self.logger.error("Cannot contact nzbget via: %s" % url)
            return
