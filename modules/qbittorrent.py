#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytunes
import cherrypy
import urllib2
import urllib
import json
import logging
from cherrypy.lib.auth2 import require

class qbittorrent:
    def __init__(self):
        self.logger = logging.getLogger('modules.qbittorrent')
        pytunes.MODULES.append({
            'name': 'qBittorrent',
            'id': 'qbittorrent',
            'test': pytunes.WEBDIR + 'qbittorrent/ping',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'qbittorrent_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'qbittorrent_name', 'placeholder':'qBittorrent'},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'qbittorrent_host', 'placeholder':'localhost'},
                {'type': 'text', 'label': 'Port *', 'name': 'qbittorrent_port', 'placeholder':'8080', 'desc':'Default is 8080'},
                {'type': 'text', 'label': 'Username', 'name': 'qbittorrent_username'},
                {'type': 'password', 'label': 'Password', 'name': 'qbittorrent_password'},
                {'type': 'bool', 'label': 'Use SSL', 'name': 'qbittorrent_ssl'}
        ]})
        
    @cherrypy.expose()
    @require()
    def index(self):
        return pytunes.LOOKUP.get_template('qbittorrent.html').render(scriptname='qbittorrent')
    
    #Get url from settings and handles auth
    @cherrypy.expose()
    @require()
    def qbturl(self):
        host = pytunes.settings.get('qbittorrent_host', '')
        port = pytunes.settings.get('qbittorrent_port',  '')
        username = pytunes.settings.get('qbittorrent_username', '')
        password = pytunes.settings.get('qbittorrent_password', '')
        ssl = 's' if pytunes.settings.get('qbittorrent_ssl', 0) else ''    
        url = 'http' + ssl +'://' + host + ':' + port + '/'        
        realm = 'Web UI Access'
        authhandler = urllib2.HTTPDigestAuthHandler()
        authhandler.add_password(realm, url, username, password)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)        
        return url
        
    #Fetches torrentlist from the client
    @cherrypy.expose()
    @require()
    def fetch(self):
        self.logger.debug("Trying to get torrents")       
        try:
            url = self.qbturl()
            return urllib2.urlopen(url + 'json/torrents/').read()        
        except Exception as e:
            self.logger.error("Couldn't get torrents %s" % e)
    
    # Gets total download and upload speed
    @cherrypy.expose()
    @require()
    def get_speed(self):
        try:
            url = self.qbturl()
            result = urllib2.urlopen(url + 'json/transferInfo/').read()
            result = json.JSONDecoder('UTF-8').decode(result)        
            speeddown = result['dl_info']
            speedup = result['up_info']        
            list_of_down = speeddown.split()
            list_of_up = speedup.split()        
            ds = list_of_down[1] + " " + list_of_down[2]
            us = list_of_up[1] + " " + list_of_up[2]        
            d = dict()
            d["qbittorrent_speed_down"] = ds
            d["qbittorrent_speed_up"] = us        
            l = []
            l.append(d)        
            return json.dumps(l)        
        except Exception as e:
            self.logger.error("Couldn't get total download and uploads speed %s" % e)

    def human_number (self, num):
        for x in [' Bytes/s',' KB/s',' MB/s',' GB/s']:
            if num < 1024.0:
                size = "%d%s" % (num, x)
                break
            num /= 1024.0
        return size

    
    # Gets total download and upload speed limits
    @cherrypy.expose()
    @require()
    def get_limits(self):
        try:
            d={}
            url = self.qbturl()
            d["qbittorrent_limit_up"] = self.human_number(int(urllib2.urlopen(url + 'command/getGlobalUpLimit').read()))
            d["qbittorrent_limit_down"] = self.human_number(int(urllib2.urlopen(url + 'command/getGlobalDlLimit').read()))
            return json.dumps(d)        
        except Exception as e:
            self.logger.error("Couldn't get total download and uploads speed limits %s" % e)
    
    # Handles pause, resume, delete, download single torrents
    @cherrypy.expose()
    @require()
    def command(self, cmd=None, hash=None, name=None):
        try:
            self.logger.debug("%s %s" %(cmd, name))
            url = self.qbturl()
            url += 'command/%s/' % cmd
            data = {}
        
            if cmd == 'delete' or cmd == 'deletePerm':
                data['hashes'] = hash
            elif cmd == 'download':
                data['urls'] = hash
            else:
                data['hash'] = hash        
            if cmd == 'resumeall' or 'pauseall':
                r = urllib2.urlopen(url + cmd)   
            data = urllib.urlencode(data)        
            result = urllib2.urlopen(url, data).read()
            return cmd + result        
        except Exception as e:
            self.logger.error("Failed at %s %s %s %s" % (cmd, name, hash ,e))
            return cmd + 'Failed'
    
    # Sets global upload and download speed
    @cherrypy.expose()
    @require()
    def set_speedlimit(self, type=None, speed=None):
        try:
            self.logger.debug("Setting %s to %s"% (type, speed))
            speed = int(speed)        
            if speed == 0:
                speed = 0            
            else:
                speed = speed * 1024
            url = self.qbturl()
            url += 'command/' + type + '/'
            data = {}
            data['limit'] = speed
            data = urllib.urlencode(data)        
            result = urllib2.urlopen(url, data)         
        except Exception as e:
            self.logger.error("Failed to set %s to %s %s"% (type, speed, e))
