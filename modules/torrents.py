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
import jsonrpclib

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
                {'type':'bool', 'label':'Enable BTN', 'name':'torrents_btn_enable'},
                {'type':'text', 'label':'BTN APIKEY', 'name':'torrents_btnapikey'},
        ]})

    @cherrypy.expose()
    def index(self, query='', **kwargs):
        #Get the active torrent providers
        torrentproviders = ['kickasstorrents']
        if pytunes.settings.get('torrents_btnapikey') and pytunes.settings.get('torrents_btn_enable') == 1:
            torrentproviders.append('BTN')

        print 'TORRENTPROVIDERS', torrentproviders

        return pytunes.LOOKUP.get_template('torrents.html').render(scriptname='torrents', torrentproviders=torrentproviders)

    @cherrypy.expose()
    def sizeof(self, num):
        for x in ['bytes','KB','MB','GB']:
            if num < 1024.0:
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def search(self, q='', engineid='', cat='', **kwargs):
        print 'Search'
        print 'q ', q
        print 'engineid', engineid
        print 'cat', cat
        #print **kwargs
        ret = ''
        row = '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
        supported_engines = ['kickasstorrents']
        if pytunes.settings.get('torrents_btnapikey') and pytunes.settings.get('torrents_btn_enable') == 1:
            supported_engines.append('BTN')
        if engineid =='kickasstorrents':
            results =  ka.search(q, cat)
            for r in results:
                icon = "<img alt='icon' src='../img/kickasstorrents.png'/>"
                link = r['link'].split('?')[0]
                dl = "<button class='btn btn-mini download' torr_link='%s' title='Send to Download'><i class='icon-download-alt'></button>" % link
                name = "<a href='" + r['desc_link'] + "' target='_blank'>" + r['name'] + "</a>"
                num = int(r['size'])
                for x in [' bytes',' KB',' MB',' GB']:
                    if num < 1024.0:
                        size = "%3.2f%s" % (num, x)
                        break
                    num /= 1024.0
                ret += row % (icon, name, size, r['seeds'], r['leech'], r['engine_url'], dl)
            return ret

        if engineid.lower() == 'btn':
            print 'zomg!'
            btn = jsonrpclib.Server('http://api.btnapps.net')
            result = btn.getTorrents(pytunes.settings.get('torrents_btnapikey', ''), q, 999)
            search_results = []
            try:
                if 'torrents' in result:
                    for k, v in result['torrents'].iteritems():
                        search_results.append(v)
                    print search_results#return search_results
                else:
                    print result #return result
            except:
                pass