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
from engines import piratebay
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
                {'type':'bool', 'label':'Enable BTN', 'name':'torrents_btn_enable'},
                {'type':'text', 'label':'BTN APIKEY', 'name':'torrents_btnapikey'},
                {'type':'bool', 'label':'The Piratebay', 'name':'torrents_piratebay_enable'},
        ]})

    def torrentproviders(self):
        torrentproviders = ['kickasstorrents','ALL']
        if pytunes.settings.get('torrents_btnapikey') and pytunes.settings.get('torrents_btn_enable') == 1:
            torrentproviders.append('BTN')
        if pytunes.settings.get('torrents_piratebay_enable') == 1:
            torrentproviders.append('the piratebay')

        return torrentproviders

    @cherrypy.expose()
    def index(self, query='', **kwargs):
        return pytunes.LOOKUP.get_template('torrents.html').render(scriptname='torrents', torrentproviders=self.torrentproviders())

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
       
        if engineid.lower() == 'kickasstorrents':
            return self.search_kickasstorrents(q, cat)
            
        elif engineid.lower() == 'btn':
            return self.search_btn(q)

        elif engineid.lower() == 'the piratebay':
            return self.search_piratebay(q)
        
        else:#else engineid.lower() == 'all':
            out = ''
            out += self.search_btn(q)
            out += self.search_kickasstorrents(q, cat)
            return out

    def search_btn(self, q, s=True): #Fcheck multicall.
        print 'running btn search'
        btn = jsonrpclib.Server('http://api.btnapps.net')
        result = btn.getTorrents(pytunes.settings.get('torrents_btnapikey', ''), q, 999)
        icon = "<img alt='icon' src='../img/btn2.png'/>"
        out = ''

        try:
            if 'torrents' in result:
                for k,v in result['torrents'].iteritems():
                    link = 'https://broadcasthe.net/torrents.php?id=%s&torrentid=%s' % (v['GroupID'], v['TorrentID'])
                    name = "<a href='" + link + "' target='_blank'>" + v['ReleaseName'] + "</a>"
                    out += html('torrent_search_table') % (icon, name, self.sizeof(int(v['Size'])), v['Seeders'], v['Leechers'], 'BTN', v['DownloadURL'])
                return out
            else:
                if result['results'] == '0':# and s:
                    self.logger.info("Couldn't find %s on BTN" % q)
                    return "<div class='alert alert-block'>Couldnt find any %s on BTN</div>" % q
                #if result['results'] == '0' and s == 'false':
                #    return
        except Exception as e:
            self.logger.error('Failed to find %s on BTN %s' % (q, e))

    def search_kickasstorrents(self, q, cat):
        print 'running kat search'
        results =  ka.search(q, cat)
        out = ''
        icon = "<img alt='icon' src='../img/kickasstorrents.png'/>"
        for r in results:
            link = r['link'].split('?')[0]
            name = "<a href='" + r['desc_link'] + "' target='_blank'>" + r['name'] + "</a>"   
            out += html('torrent_search_table') % (icon, name, self.sizeof(int(r['size'])), r['seeds'], r['leech'], r['engine_url'], link)
        return out

    def search_piratebay(self, q, cat='ALL'):

        results = piratebay.piratebay()
        print results.search(q)
        print results

