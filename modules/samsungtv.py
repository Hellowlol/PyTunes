#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
import logging
import socket
import base64


class Samsungtv:
    def __init__(self):
        self.logger = logging.getLogger('modules.samsungtv')
        pytunes.MODULES.append({
            'name': 'Samsung tvremote',
            'id': 'samsungtv',
            #'test': pytunes.WEBDIR + 'sickbeard/ping',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'samsungtv_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'samsungtv_name'},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'samsungtv_host'},
                {'type': 'text', 'label': 'Tv model', 'name': 'samsungtv_model'},
                {'type': 'text', 'label': 'Htpc-Manager MAC', 'name': 'samsung_htpcmac'},
                {'type': 'text', 'label': 'HTPC-Manager IP', 'name': 'samsung_htpchost'}
               
        ]})
    
    @cherrypy.expose()
    def index(self):
        return pytunes.LOOKUP.get_template('samsungtv.html').render(scriptname='samsungtv')
    
    @cherrypy.expose()
    def sendkey(self, action):
        try:
            #key = None
            key = action
            print 'action: ', action
            print 'key: ', key
            if key == 'undefined':
                pass
            else:
                src = pytunes.settings.get('samsung_htpchost', '')
                mac = pytunes.settings.get('samsung_htpcmac', '')
                remote = 'Pytunes remote'
                dst = pytunes.settings.get('samsungtv_host', '')
                application = 'python'
                tv  = pytunes.settings.get('samsungtv_model', '')
    
                new = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new.connect((dst, 55000))
                msg = chr(0x64) + chr(0x00) +\
                    chr(len(base64.b64encode(src)))    + chr(0x00) + base64.b64encode(src) +\
                    chr(len(base64.b64encode(mac)))    + chr(0x00) + base64.b64encode(mac) +\
                    chr(len(base64.b64encode(remote))) + chr(0x00) + base64.b64encode(remote)
                pkt = chr(0x00) +\
                    chr(len(application)) + chr(0x00) + application +\
                    chr(len(msg)) + chr(0x00) + msg
                new.send(pkt)
                msg = chr(0x00) + chr(0x00) + chr(0x00) +\
                chr(len(base64.b64encode(key))) + chr(0x00) + base64.b64encode(key)
                pkt = chr(0x00) +\
                    chr(len(tv))  + chr(0x00) + tv +\
                    chr(len(msg)) + chr(0x00) + msg
                new.send(pkt)
                new.close()
        except Exception as e:
            print e
            self.logger.debug('Failed to send %s to the tv' % key)