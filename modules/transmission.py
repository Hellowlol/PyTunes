#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
import urllib2
import base64
from json import loads, dumps
import logging
from cherrypy.lib.auth2 import require

class Transmission:
    # Transmission Session ID
    sessionId = ''

    def __init__(self):
        self.logger = logging.getLogger('modules.transmission')
        pytunes.MODULES.append({
            'name': 'Transmission',
            'id': 'transmission',
            'test': pytunes.WEBDIR + 'transmission/ping',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'transmission_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'transmission_name', 'placeholder':''},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'transmission_host', 'placeholder':''},
                {'type': 'text', 'label': 'Port *', 'name': 'transmission_port', 'placeholder':'', 'desc':'Default is 9091'},
                {'type': 'text', 'label': 'Username', 'name': 'transmission_username'},
                {'type': 'password', 'label': 'Password', 'name': 'transmission_password'}
        ]})

    @cherrypy.expose()
    @require()
    def index(self):
        return pytunes.LOOKUP.get_template('transmission.html').render(scriptname='transmission')


    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def queue(self):
        fields = ['id', 'name', 'status', 'comment', 'downloadDir', 'downloadDir', 'percentDone', 'isFinished', 'eta', 'rateDownload', 'rateUpload', 'uploadRatio']
        return self.fetch('torrent-get', {'fields': fields})

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def stats(self):
        return self.fetch('session-stats')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def start(self, torrentId = False):
        if (torrentId == False) :
            return self.fetch('torrent-start-now')
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-start-now', {'ids': torrentId})

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def stop(self, torrentId = False):
        if (torrentId == False) :
            return self.fetch('torrent-stop')
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-stop', {'ids': torrentId})

    #For torrent search
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def to_client(self, link, torrentname, **kwargs):
        try:
            self.logger.info('Added %s to uTorrent' % torrentname)
            return self.fetch('torrent-add', {'filename': link})
        except Exception as e:
            self.logger.debug('Failed to add %s to uTorrent %s %s'(torrentname, link, e))


    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def remove(self, torrentId):
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-remove', {'ids': torrentId})

    # Wrapper to access the Transmission Api
    # If the first call fails, there probably is no valid Session ID so we try it again
    def fetch(self, method, arguments=''):
        """ Do request to Transmission api """
        self.logger.debug("Request transmission method: "+method)

        host = pytunes.settings.get('transmission_host', '')
        port = str(pytunes.settings.get('transmission_port', ''))

        url = 'http://' +  host + ':' + str(port) + '/transmission/rpc/'

        # format post data
        data = {'method': method}
        if (arguments != ''):
            data['arguments'] =  arguments
        data = dumps(data)

        # Set Header
        header = {
            'X-Transmission-Session-Id': self.sessionId,
            'Content-Type': 'json; charset=UTF-8'
        }

        # Add authentication
        authentication = self.auth()
        if (authentication) :
            header['Authorization'] = "Basic %s" % authentication

        try:
            request = urllib2.Request(url, data=data, headers=header)
            response = urllib2.urlopen(request).read()
            return loads(response)
        except urllib2.HTTPError, e:
             # Fetching url failed Maybe Transmission session must be renewed
            if (e.getcode() == 409 and e.headers['X-Transmission-Session-Id']) :
                self.logger.debug("Setting new session ID provided by Transmission")

                # If response is 409 re-set session id from header
                self.sessionId = e.headers['X-Transmission-Session-Id']

                self.logger.debug("Retry Transmission api with new session id.")
                try:
                    header['X-Transmission-Session-Id'] = self.sessionId

                    req = urllib2.Request(url, data=data, headers=header)
                    response = urllib2.urlopen(req).read()
                    return loads(response)
                except:
                    self.logger.error("Unable access Transmission api with new session id.")
                    return
        except Exception:
            self.logger.error("Unable to fetch information from: " + url)
            return


    # Construct url with login details
    def auth(self):
        """ Generate a base64 HTTP auth string based on settings """
        self.logger.debug("Generating authentication string for transmission")

        password = pytunes.settings.get('transmission_password', '')
        username = pytunes.settings.get('transmission_username', '')

        if username != '' and password != '':
            return base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

        return False
