#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
from pytunes.proxy import get_image
import json
from urllib2 import urlopen
from urllib import quote_plus
import logging
import hashlib


class Couchpotato:
    def __init__(self):
        self.logger = logging.getLogger('modules.couchpotato')
        pytunes.MODULES.append({
            'name': 'CouchPotato',
            'id': 'couchpotato',
            'test': pytunes.WEBDIR + 'couchpotato/getapikey',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'couchpotato_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'couchpotato_name', 'placeholder':''},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'couchpotato_host', 'placeholder':'localhost'},
                {'type': 'text', 'label': 'Username *', 'name': 'couchpotato_username', 'placeholder':''},
                {'type': 'text', 'label': 'Password *', 'name': 'couchpotato_password', 'placeholder':''},
                {'type': 'text', 'label': 'Port *', 'name': 'couchpotato_port', 'placeholder':'', 'desc':'Default is 5050'},
                {'type': 'text', 'label': 'Basepath', 'name': 'couchpotato_basepath'},
                {'type': 'text', 'label': 'API key', 'name': 'couchpotato_apikey', 'desc': 'Press test button to get apikey'},
                {'type': 'bool', 'label': 'Use SSL', 'name': 'couchpotato_ssl'}
        ]})

    @cherrypy.expose()
    def index(self):
        return pytunes.LOOKUP.get_template('couchpotato.html').render(scriptname='couchpotato')

    @cherrypy.expose()
    def webinterface(self):
        """ Generate page from template """
        ssl = 's' if pytunes.settings.get('couchpotato_ssl', 0) else ''
        host = pytunes.settings.get('couchpotato_host', '')
        port = str(pytunes.settings.get('couchpotato_port', ''))
        basepath = pytunes.settings.get('couchpotato_basepath', '/')
        if not(basepath.endswith('/')):
            basepath += "/"
        url = 'http' + ssl + '://' + host + ':' + port + basepath
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def ping(self, couchpotato_host, couchpotato_port, couchpotato_apikey, couchpotato_basepath, couchpotato_ssl=False, **kwargs):
        self.logger.debug("Testing connectivity to couchpotato")
        if not(couchpotato_basepath.endswith('/')):
            couchpotato_basepath += "/"

        ssl = 's' if couchpotato_ssl else ''
        url = 'http' + ssl + '://' + couchpotato_host + ':' + couchpotato_port + couchpotato_basepath + 'api/' + couchpotato_apikey
        try:
            return json.loads(urlopen(url + '/app.available/', timeout=10).read())
        except:
            self.logger.error("Unable to connect to couchpotato")
            self.logger.debug("connection-URL: " + url)
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def getapikey(self, couchpotato_username, couchpotato_password, couchpotato_host, couchpotato_port, couchpotato_apikey, couchpotato_basepath, couchpotato_ssl=False, **kwargs):
        self.logger.debug("Testing connectivity to couchpotato")
        if couchpotato_password and couchpotato_username != '':
            couchpotato_password = hashlib.md5(couchpotato_password).hexdigest()
            couchpotato_username = hashlib.md5(couchpotato_username).hexdigest()
            
        getkey = 'getkey/?p=%s&u=%s' % (couchpotato_password, couchpotato_username)
        
        if not(couchpotato_basepath.endswith('/')):
            couchpotato_basepath += "/"
    
        ssl = 's' if couchpotato_ssl else ''
        url = 'http' + ssl + '://' + couchpotato_host + ':' + couchpotato_port + couchpotato_basepath + getkey
        try:
            return json.loads(urlopen(url, timeout=2).read())
        except:
            self.logger.error("Unable to connect to couchpotato")
            self.logger.debug("connection-URL: " + url)
            return json.loads(urlopen(url, timeout=2).read())

    @cherrypy.expose()
    def GetImage(self, url, h=None, w=None, o=100):
        return get_image(url, h, w, o)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetMovieList(self, status='', limit='', search='', starts_with=''):
        self.logger.debug("Fetching Movies")
        if status == 'done':
            status = 'done&release_status=done&status_or=1'
        if search:
            search = '&search=%s' % quote_plus(search)
        if starts_with:
            starts_with = '&starts_with=%s' % starts_with
        status = 'type=movie&status=%s&limit_offset=%s%s%s' % (status, limit, search, starts_with)
        return self.fetch('movie.list/?' + status)

        

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetNotificationList(self, limit='20'):
        self.logger.debug("Fetching Notification")
        data = self.fetch('notification.list/?limit_offset=' + limit)
        self.fetch('notification.markread')
        return data

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def SearchMovie(self, q=''):
        self.logger.debug("Searching for movie")
        return self.fetch('movie.search/?q=' + q)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def AddMovie(self, movieid, profile, title):
        self.logger.debug("Adding movie")
        return self.fetch('movie.add/?profile_id=' + profile + '&identifier=' + movieid + '&title=' + title)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def EditMovie(self, id, profile, title):
        self.logger.debug("Editing movie")
        return self.fetch('movie.edit/?id=' + id + '&profile_id=' + profile + '&default_title=' + title)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def RefreshMovie(self, id):
        self.logger.debug("Refreshing movie")
        return self.fetch('movie.refresh/?id=' + id)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def DeleteMovie(self, id=''):
        self.logger.debug("Deleting movie")
        return self.fetch('movie.delete/?id=' + id)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetReleases(self, id=''):
        self.logger.debug("Downloading movie")
        return self.fetch('media.get/?id=' + id)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def DownloadRelease(self, id=''):
        self.logger.debug("Downloading movie")
        return self.fetch('release.download/?id=' + id)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def IgnoreRelease(self, id=''):
        self.logger.debug("Downloading movie")
        return self.fetch('release.ignore/?id=' + id)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetProfiles(self):
        self.logger.debug("Fetching available profiles")
        return self.fetch('profile.list/')

    def fetch(self, path):
        try:
            host = pytunes.settings.get('couchpotato_host', '')
            port = str(pytunes.settings.get('couchpotato_port', ''))
            apikey = pytunes.settings.get('couchpotato_apikey', '')
            basepath = pytunes.settings.get('couchpotato_basepath', '/')
            ssl = 's' if pytunes.settings.get('couchpotato_ssl', 0) else ''

            if not(basepath.endswith('/')):
                basepath += "/"

            url = 'http' + ssl + '://' + host + ':' + port + basepath + 'api/' + apikey + '/' + path

            self.logger.debug("Fetching information from: " + url)
            return json.loads(urlopen(url, timeout=10).read())
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch information")
            return
