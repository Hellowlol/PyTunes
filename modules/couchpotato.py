#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
from pytunes.proxy import get_image
import json
import requests
from urllib import quote_plus
import logging
import hashlib
from cherrypy.lib.auth2 import require


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
                {'type': 'text', 'label': 'IP / Host *', 'name': 'couchpotato_host', 'placeholder':''},
                {'type': 'text', 'label': 'Username *', 'name': 'couchpotato_username', 'placeholder':''},
                {'type': 'text', 'label': 'Password *', 'name': 'couchpotato_password', 'placeholder':''},
                {'type': 'text', 'label': 'Port *', 'name': 'couchpotato_port', 'placeholder':'', 'desc':'Default is 5050'},
                {'type': 'text', 'label': 'Basepath', 'name': 'couchpotato_basepath'},
                {'type': 'text', 'label': 'API key', 'name': 'couchpotato_apikey', 'desc': 'Press test button to get apikey'},
                {'type': 'bool', 'label': 'Use SSL', 'name': 'couchpotato_ssl'}
        ]})

    @cherrypy.expose()
    @require()
    def index(self):
        return pytunes.LOOKUP.get_template('couchpotato.html').render(scriptname='couchpotato')

    @cherrypy.expose()
    @require()
    def webinterface(self):
        """ Generate page from template """
        ssl = 's' if pytunes.settings.get('couchpotato_ssl', 0) else ''
        host = pytunes.settings.get('couchpotato_host', '')
        port = str(pytunes.settings.get('couchpotato_port', ''))
        basepath = pytunes.settings.get('couchpotato_basepath', '/')
        if not(basepath.endswith('/')):
            basepath += "/"
        url = 'http%s://%s:%s%s' % (ssl, host, port, basepath)
        raise cherrypy.HTTPRedirect(url)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def ping(self, couchpotato_host, couchpotato_port, couchpotato_apikey, couchpotato_basepath, couchpotato_ssl=False, **kwargs):
        self.logger.debug("Testing connectivity to couchpotato")
        if not(couchpotato_basepath.endswith('/')):
            couchpotato_basepath += "/"

        ssl = 's' if couchpotato_ssl else ''
        url = 'http%s://%s:%s%sapi/%s' % (ssl, couchpotato_host, couchpotato_port, couchpotato_basepath, couchpotato_apikey)
        try:
            f = requests.get('%s/app.available/' % url, timeout= 10)
            return f.json()
        except:
            self.logger.error("Unable to connect to couchpotato")
            self.logger.debug("connection-URL: %s" % url)
            return

    @cherrypy.expose()
    @require()
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
        url = 'http%s://%s:%s%s%s' % (ssl, couchpotato_host, couchpotato_port, couchpotato_basepath, getkey)
        try:
            f = requests.get(url, timeout=2)
            return f.json()
        except:
            self.logger.error("Unable to connect to couchpotato")
            self.logger.debug("connection-URL: %s" % url)
            return

    @cherrypy.expose()
    @require()
    def GetImage(self, url, h=None, w=None, o=100):
        return get_image(url, h, w, o)

    @cherrypy.expose()
    @require()
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
        return self.fetch('movie.list/?%s' % status)

        

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetNotificationList(self, limit='20'):
        self.logger.debug("Fetching Notification")
        data = self.fetch('notification.list/?limit_offset=%s' % limit)
        self.fetch('notification.markread')
        return data

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def SearchMovie(self, q=''):
        self.logger.debug("Searching for movie")
        return self.fetch('movie.search/?q=%s' % q)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def AddMovie(self, movieid, profile, title):
        self.logger.debug("Adding movie")
        return self.fetch('movie.add/?profile_id=%s&identifier=%s&title=%s' % (profile, movieid, title))

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def EditMovie(self, id, profile, title):
        self.logger.debug("Editing movie")
        return self.fetch('movie.edit/?id=%s&profile_id=%s&default_title=%s' % (id, profile, title))

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def RefreshMovie(self, id):
        self.logger.debug("Refreshing movie")
        return self.fetch('movie.refresh/?id=%s' % id)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def DeleteMovie(self, id=''):
        self.logger.debug("Deleting movie")
        return self.fetch('movie.delete/?id=%s' % id)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetReleases(self, id=''):
        self.logger.debug("Downloading movie")
        return self.fetch('media.get/?id=%s' % id)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def DownloadRelease(self, id=''):
        self.logger.debug("Downloading movie")
        return self.fetch('release.download/?id=%s' % id)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def IgnoreRelease(self, id=''):
        self.logger.debug("Downloading movie")
        return self.fetch('release.ignore/?id=%s' % id)

    @cherrypy.expose()
    @require()
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

            url = 'http%s://%s:%s%s%sapi/%s/%s' % (ssl, host, port, basepath, apikey, path)

            self.logger.debug("Fetching information from: %s" % url)
            f = requests.get(url, timeout=10, stream=True)
            return f.json()
        except Exception, e:
            self.logger.debug("Exception: %s" % str(e))
            self.logger.debug(path)
            self.logger.error("Unable to fetch information")
            return
