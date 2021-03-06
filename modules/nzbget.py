#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
from urllib import quote
from urllib2 import urlopen, Request
from json import loads
import logging
import base64
from jsonrpclib import jsonrpc


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
                {'type': 'text', 'label': 'IP / Host', 'placeholder':'localhost', 'name': 'nzbget_host'},
                {'type': 'text', 'label': 'Port', 'placeholder':'6789', 'name': 'nzbget_port'},
                {'type': 'text', 'label': 'Basepath', 'placeholder':'/nzbget', 'name': 'nzbget_basepath'},
                {'type': 'text', 'label': 'User', 'name': 'nzbget_username'},
                {'type': 'password', 'label': 'Password', 'name': 'nzbget_password'},
                {'type': 'bool', 'label': 'Use SSL', 'name': 'nzbget_ssl'}
        ]})

    @cherrypy.expose()
    def index(self):
        return pytunes.LOOKUP.get_template('nzbget.html').render(scriptname='nzbget')

    @cherrypy.expose()
    def nzbget_url(self):
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
        if username and  password:
            authstring = '%s:%s@' % (username, password)
        else:
            authstring = ''

        url = 'http%s://%s:%s%sjsonrpc/' % (ssl, authstring, host, port, nzbget_basepath)
        return url


    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def version(self, nzbget_host, nzbget_basepath, nzbget_port, nzbget_username, nzbget_password, nzbget_ssl=False, **kwargs):
        self.logger.debug("Fetching version information from nzbget")
        ssl = 's' if nzbget_ssl else ''

        if(nzbget_basepath == ""):
            nzbget_basepath = "/"
        if not(nzbget_basepath.endswith('/')):
            nzbget_basepath += "/"

        url = 'http' + ssl + '://'+  nzbget_host + ':' + nzbget_port + nzbget_basepath + 'jsonrpc/version'
        url = 'http%s://%s:%s%sjsonrpc/version' % (ssl,  nzbget_host, nzbget_port, nzbget_basepath)
        try:
            request = Request(url)
            if(nzbget_username != ""):
                base64string = base64.encodestring(nzbget_username + ':' + nzbget_password).replace('\n', '')
                request.add_header("Authorization", "Basic %s" % base64string)
            self.logger.debug("Fetching information from: " + url)
            return loads(urlopen(request, timeout=10).read())
        except:
            self.logger.error("Unable to contact nzbget via %s" % url)
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetHistory(self):
        try:
            self.logger.debug("Fetching history")
            nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
            return nzbget.history()
        except Exception as e:
            self.logger.error("Failed to get history %s" % e)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def AddNzbFromUrl(self, nzb_url= '', nzb_category='', nzb_name='') : 
        if not nzb_url:
            return
        self.logger.info("Added %s category %s url %s" %(nzb_name, nzb_category, nzb_url))
        try:
            nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
            nzb = urlopen(nzb_url).read()
            # If name is missig the link is added manually
            if not nzb_name:
                nzb_name = 'Temp Name'
            nzbget.append(nzb_name, nzb_category, False, base64.standard_b64encode(nzb))
            return {'status':True}
        except Exception as e:
            self.logger.error("Failed to add %s to queue %s" % (nzb_name, e))

    #Used to grab the categories from the config
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetConfig(self):
        nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
        return nzbget.config()

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetWarnings(self):
        try:
            self.logger.debug("Fetching warnings")
            nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
            return nzbget.log(0, 1000)
        except Exception as e:
            self.logger.error("Failed to fetch warnings %s" % e)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def queue(self):
        try:
            self.logger.debug("Fetching queue")
            nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
            return nzbget.listgroups()
        except Exception as e:
            self.logger.error("Failed to fetch queue %s" % e)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def status(self):
        try:
            self.logger.debug("Fetching status")
            nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
            return nzbget.status()
        except Exception as e:
            self.logger.error("Failed to fetch queue %s" % e)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def QueueAction(self, action):
        try:
            self.logger.debug(action + " ALL")
            nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
            if 'resume' in action:
                status = nzbget.resume()
            elif 'pause' in action:
                status = nzbget.pause()
            return status
        except Exception as e:
            self.logger.error("Failed to %s %s" % (action, e))

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def IndividualAction(self, id='', name='', action=''):
        try:
            self.logger.debug("%s %s %s" % (action, name, id))
            nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
            if 'resume' in action:
                action = 'GroupResume'
            elif 'pause' in action:
                print 'pause is pause'
                action = 'GroupPause'
            elif 'delete' in action:
                action = 'GroupDelete'
            elif 'hidehistory' in action:
                action = 'HistoryDelete'
            status = nzbget.editqueue(action, 0, '', [int(id)])
            return status
        except Exception as e:
            self.logger.error("Failed to %s %s %s %s" % (action, name, id, e))



    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def SetSpeed(self, speed):
        try:
            self.logger.debug("Setting speed-limit %s" % speed)
            nzbget = jsonrpc.ServerProxy('%s/jsonrpc' % self.nzbget_url())
            return nzbget.rate(int(speed))
        except Exception as e:
            self.logger.error("Failed to set speed to %s %s" % (speed, e))


