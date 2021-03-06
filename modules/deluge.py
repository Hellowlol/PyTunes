#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback
import sys
import os
import cherrypy
import pytunes
import urllib2
import gzip
import socket
from json import loads, dumps
import logging
import cookielib
from StringIO import StringIO

class Deluge:

    cookieJar = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))


    def __init__(self):
        self.logger = logging.getLogger('modules.deluge')
        pytunes.MODULES.append({
            'name': 'Deluge',
            'id': 'deluge',
            'test': pytunes.WEBDIR + 'deluge/ping',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'deluge_enable', 'desc': 'Change Requires Restart'},
                {'type': 'text', 'label': 'Menu name', 'name': 'deluge_name'},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'deluge_host'},
                {'type': 'text', 'label': 'Port *', 'name': 'deluge_port'},
                {'type': 'password', 'label': 'Password', 'name': 'deluge_password'}
        ]})

    @cherrypy.expose()
    def index(self):
        return pytunes.LOOKUP.get_template('deluge.html').render(scriptname='deluge')

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def connected(self):
        return self.fetch('web.connected')

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def connect(self,hostid):
        return self.fetch('web.connect',[hostid])

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def get_hosts(self):
        return self.fetch('web.get_hosts')

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def queue(self):
        fields = ['progress','is_finished','ratio','name','download_payload_rate','upload_payload_rate','eta','state','hash','total_size']
        return self.fetch('core.get_torrents_status', [[],fields])

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def stats(self):
        fields = ["payload_download_rate","payload_upload_rate"]
        return self.fetch('core.get_session_status',[fields])

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def start(self, torrentId):
        torrents = [torrentId]
        return self.fetch('core.resume_torrent', [torrents])

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def stop(self, torrentId):
        torrents = [torrentId]
        return self.fetch('core.pause_torrent',[torrents])

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def remove(self, torrentId, removeData):
        removeDataBool = bool(int(removeData))
        return self.fetch('core.remove_torrent', [torrentId,removeDataBool])

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def to_client(self, link, torrentname=None, **kwargs):
        try:
            #Fetch download path from settings
            download_path = self.fetch('core.get_config_value', ['download_location'])
            #Download the torrent from zhe interwebz
            get_url = self.fetch('web.download_torrent_from_url', [link])
            #Load temp torrent in client
            self.logger.info('Added %s to deluge' % torrentname)
            return self.fetch('web.add_torrents', [[{'path': get_url['result'], 'options': {'download_location': download_path['result']}}]])
        except Exception as e:
            self.logger.debug('Failed adding %s to deluge %s %s' % (torrentname, link, e))

    # Wrapper to access the Deluge Api
    # If the first call fails, there probably is no valid Session ID so we try it again
    def fetch(self, method, arguments=[]):
        """ Do request to Deluge api """
        self.logger.debug("Request deluge method: "+method)

        # format post data
        data = {'id':1,'method': method,'params':arguments}


        response = self.read_data(data)
        print "response: ", response
        self.logger.debug ("response is %s" %response)
        if response and response['error']:
            self.auth()
            response = self.read_data(data)
            self.logger.debug ("response is %s" %response)
            print "response is %s" %response
        return response

    def auth(self):
        self.read_data({"method": "auth.login","params": [pytunes.settings.get('deluge_password', '')],"id": 1})


    def read_data(self,data):
        try:
            self.logger.debug("Read data from server. Data:%s" % data)

            host = pytunes.settings.get('deluge_host', '')
            port = str(pytunes.settings.get('deluge_port', ''))

            url = 'http://' +  host + ':' + str(port) + '/json'
            print 'url: ', url
            post_data = dumps(data)
            buf = StringIO( self.opener.open(url, post_data,1).read())
            f = gzip.GzipFile(fileobj=buf)
            response = loads(f.read())
            self.logger.debug ("response for %s is %s" %(data,response))
            return response
        except urllib2.URLError:
            self.logger.error ("can't connect with %s" %data)
            return {'result':{},'error':"can't connect with %s" %data}
        except socket.timeout:
            self.logger.error ("timeout when connect with %s" %data)
            return {'result':{},'error':"can't connect with %s" %data}
