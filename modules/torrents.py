#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
import glob
import os
import sys
from pytunes import staticvars
from pytunes.proxy import get_image
from urllib2 import urlopen, quote
from json import loads
import logging
import xml.etree.ElementTree as xml
from engines import ka
from engines import btn
#from engines import piratebay
from engines import fenopy
import jsonrpclib
from pytunes.staticvars import get_var as html

class Torrents:
    def __init__(self):
        self.logger = logging.getLogger('modules.torrents')
        pytunes.MODULES.append({
            'name': 'Torrent Search',
            'id': 'torrents',
            'fields': [
                {'type':'bool', 'label':'Enable', 'name':'torrents_enable'},
                {'type':'text', 'label':'Menu name', 'name':'torrents_name'},
                {'type':'text', 'label':'Seeds', 'name':'torrents_seeds', 'value':'5', 'desc':'Minimum Number of Seeders'},
                {'type':'bool', 'label':'Enable BTN', 'name':'torrents_btn_enabled'},
                {'type':'text', 'label':'BTN APIKEY', 'name':'torrents_btnapikey'},
                {'type':'bool', 'label':'The Piratebay', 'name':'torrents_piratebay_enabled'},
                {'type':'bool', 'label':'Fenopy', 'name':'torrents_fenopy_enabled'},
                {'type':'bool', 'label':'Fenopy verified torrents only', 'name':'torrents_fenopy_enabled_verified'},
        ]})

    def torrentproviders(self):
        torrentproviders = ['kickasstorrents','ALL']
        if pytunes.settings.get('torrents_btnapikey') and pytunes.settings.get('torrents_btn_enabled') == 1:
            torrentproviders.append('BTN')

        if pytunes.settings.get('torrents_fenopy_enabled') == 1:
            torrentproviders.append('fenopy')

        return torrentproviders

    @cherrypy.expose()
    def index(self, query='', **kwargs):
        return pytunes.LOOKUP.get_template('torrents.html').render(scriptname='torrents', torrentproviders=self.torrentproviders())

    @cherrypy.expose()
    def sizeof(self, num):
        for x in ['bytes','KB','MB','GB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
        return "%3.1f %s" % (num, 'TB')

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def search(self, q='', engineid='', cat='', **kwargs):

        print 'Searching with %s' % engineid
        if engineid.lower() == 'kickasstorrents':
            return self.search_kickasstorrents(q, cat)
            
        elif engineid.lower() == 'btn':
            return self.search_btn(q, cat)

        elif engineid.lower() == 'the piratebay':
            return self.search_piratebay(q)

        elif engineid.lower() == 'fenopy':
            return self.search_fenopy(q,cat)
        
        elif engineid.lower() == 'all':
            out = ''
            out += self.search_btn(q, cat)
            out += self.search_kickasstorrents(q, cat)
            out += self.search_fenopy(q, cat)
            #out += self.search_piratebay(q)#Does not work
            return out

    #Checkmulti call btn, should not run unless explisit btn provider or all and cat tv.
    def search_btn(self, q, cat):
        return btn.search(q, cat)

    def search_kickasstorrents(self, q, cat):
        results =  ka.search(q, cat)
        out = ''
        icon = "<img alt='icon' src='../img/kickasstorrents.png'/>"
        for r in results:
            link = r['link'].split('?')[0]
            name = "<a href='" + r['desc_link'] + "' target='_blank'>" + r['name'] + "</a>"   
            out += html('torrent_search_table') % (icon, name, self.sizeof(int(r['size'])), r['seeds'], r['leech'], r['engine_url'], link)
        return out

    def search_fenopy(self, q, cat):
        results = fenopy.search(q, cat)
        out = ''
        icon = "<img alt='icon' src='../img/kickasstorrents.png'/>"
        verified = pytunes.settings.get('torrents_fenopy_enabled_verified')
        for t in results:
            if verified and t['verified'] != 1:
                continue
            name = "<a href='" + t['page'] + "' target='_blank'>" + t['name'] + "</a>"
            out += html('torrent_search_table') % (icon, name, self.sizeof(t['size']), t['seeder'], t['leecher'], 'Fenopy', t['torrent'])
        return out 

    ''' #does not work
    def search_piratebay(self, q):
        s = piratebay.piratebay()
        results = s.search(s)
        icon = "<img alt='icon' src='../img/kickasstorrents.png'/>"
        out = ''
        for r in results:
            name = "<a href='" + r['desc_link'] + "' target='_blank'>" + r['name'] + "</a>"   
            out += html('torrent_search_table') % (icon, name, r['size'], r['seeds'], r['leech'], r['engine_url'], r['link'])
        return out
    '''

