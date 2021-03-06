#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
import math
from pytunes.proxy import get_image
from urllib2 import urlopen, quote
from json import loads
import logging

class Newznab:
    def __init__(self):
        self.logger = logging.getLogger('modules.newznab')
        pytunes.MODULES.append({
            'name': 'Newznab Search',
            'id': 'newznab',
            'fields': [
                {'type':'bool', 'label':'Enable', 'name':'newznab_enable'},
                {'type':'text', 'label':'Menu name', 'name':'newznab_name', 'placeholder':''},
                #{'type':'select',
                # 'label':'Default NZB Client',
                # 'name':'default_nzb_id',
                # 'options':[],
                # 'desc':'Only Enabled Clients Will Show' 
                #},
                {'type':'text', 'label':'Console Category', 'name':'newznab_console', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Movies Category', 'name':'newznab_movies', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Audio Category', 'name':'newznab_audio', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'PC Category', 'name':'newznab_pc', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'TV Category', 'name':'newznab_tv', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'XXX Category', 'name':'newznab_xxx', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Books Category', 'name':'newznab_books', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Other Category', 'name':'newznab_other', 'desc':'From Sabnzbd Configuration'}
        ]})

        pytunes.MODULES.append({
            'name': 'Newznab Servers',
            'id': 'newznab_update_server',
            'action': '%ssettings/setnewzserver' % pytunes.WEBDIR,
            #'test': pytunes.WEBDIR + 'newznab/ping',
            'fields': [
                {'type':'select',
                 'label':'Newznab Servers',
                 'name':'newznab_server_id',
                 'options':[
                    {'name':'New', 'value':0}
                ]},
                {'type':'text',
                 'label':'Name',
                 'name':'newznab_server_name'},
                {'type':'text', 'label':'Host', 'name':'newznab_server_host'},
                {'type':'text', 'label':'Apikey', 'name':'newznab_server_apikey'},
                {'type':'bool', 'label':'Use SSL', 'name':'newznab_server_ssl'}
        ]})

    @cherrypy.expose()
    def index(self, query='', **kwargs):
        return pytunes.LOOKUP.get_template('newznab.html').render(query=query, scriptname='newznab')

    """
    NOT IMPLEMENTET
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def ping(self, newznab_host, newznab_apikey, **kwargs):
        self.logger.debug("Pinging newznab-host")
        return 1
    """

    @cherrypy.expose()
    def thumb(self, url, h=None, w=None, o=100):
        if url.startswith('rageid'):
            settings = pytunes.settings
            host = settings.get('newznab_host', '').replace('http://', '').replace('https://', '')
            ssl = 's' if settings.get('newznab_ssl', 0) else ''

            url = 'http%s://%s/covers/tv/%s.jpg' % (ssl, host, url[6:])

        return get_image(url, h, w, o)

    @cherrypy.expose()
    def getcategories(self, **kwargs):
        self.logger.debug("Fetching available categories")
        ret = ''
        try:
            settings = pytunes.settings
            self.current = settings.get_current_newznab_host()
            host = self.current.host.replace('http://', '').replace('https://', '')
            ssl = '' if self.current.ssl == '0' else 's'
            apikey = self.current.apikey
            url = 'http%s://%s/api?t=caps&o=xml' % (ssl, host)
            self.logger.debug("Fetching Cat information from: %s" % url)
            caps = urlopen(url, timeout=10).read()
            lines = caps.split('\n')
            opt_line = '<option value="%s">%s</option>'
            for line in lines:
                if 'category' in line and 'genre' not in line and not '/cat' in line:
                    junk,id,name = line.strip().split(' ')
                    id = id.split('"')[1]
                    main_name = name.split('"')[1]
                    ret += opt_line % (id, main_name)
                if 'subcat' in line:
                    subcat = line.strip().split(' name')
                    id = subcat[0].split('"')[1]
                    name = '%s > %s' % (main_name, subcat[1].split('"')[1])
                    ret += opt_line % (id, name)
        except:
            self.logger.error('Unable to fetch categories from: %s' % url)
        return ret

    @cherrypy.expose()
    def search(self, q='', cat='', **kwargs):
        ret = ''
        row = '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
        settings = pytunes.settings
        sab_cat = {
            '1000':settings.get('newznab_console', ''),
            '2000':settings.get('newznab_movies', ''),
            '3000':settings.get('newznab_audio', ''),
            '4000':settings.get('newznab_pc', ''),
            '5000':settings.get('newznab_tv', ''),
            '6000':settings.get('newznab_xxx', ''),
            '7000':settings.get('newznab_books', ''),
            '8000':settings.get('newznab_other', '')
        }        
        if cat:
            cat = '&cat=%s' % cat
        res = self.fetch('search&q=%s%s&extended=1' % (quote(q), cat))
        #put in staticvars
        link = "<a href='/newznab/AddNzbFromUrl?nzb_url=%s&nzb_category=%s' class='ajax-link' title='Download' cat='%s'><i class='icon-download-alt'></i></a>"
        try:
            results = res['channel']['item']
        except:
            results = res
        grabs = '0'
        for each in results:
            files = str(each['attr'][4]['@attributes']['value'])
            grabs = str(each['attr'][6]['@attributes']['value'])
            category = each['category']
            title = each['title']
            cat = sab_cat[str(each['attr'][0]['@attributes']['value'])]
            num = int(each['enclosure']['@attributes']['length'])
            for x in [' bytes',' KB',' MB',' GB']:
                if num < 1024.0:
                    size = "%3.2f%s" % (num, x)
                    break
                num /= 1024.0
            dl = link % (quote(each['link']), cat, cat)
            ret += row % (title, category, size, files, grabs, dl)
        return ret

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def AddNzbFromUrl(self, nzb_url, nzb_category=''):
        self.logger.debug("Adding nzb from url")
        if nzb_category:
            nzb_category = '&cat=%s' % nzb_category
        return self.send('&mode=addurl&name=%s%s' % (quote(nzb_url), nzb_category))

    def fetch(self, cmd):
        try:
            settings = pytunes.settings
            self.current = settings.get_current_newznab_host()
            host = self.current.host.replace('http://', '').replace('https://', '')
            ssl = 's' if settings.get('newznab_ssl') == 'on' else ''
            apikey = self.current.apikey
            url = 'http%s://%s/api?o=json&apikey=%s&t=%s' ( ssl, host, apikey, cmd)
            self.logger.debug("Fetching information from: %s" % url)
            return loads(urlopen(url, timeout=30).read())
        except Exception, e:
            self.logger.debug("Exception%s: " % str(e))
            self.logger.error("Unable to fetch information from: newznab %s" % str(e))

    def send(self, link):
        try:
            host = pytunes.settings.get('sabnzbd_host', '')
            port = str(pytunes.settings.get('sabnzbd_port', ''))
            apikey = pytunes.settings.get('sabnzbd_apikey', '')
            sabnzbd_basepath = pytunes.settings.get('sabnzbd_basepath', '/sabnzbd/')
            ssl = 's' if pytunes.settings.get('sabnzbd_ssl', 0) else ''

            if(sabnzbd_basepath == ""):
                sabnzbd_basepath = "/sabnzbd/"
            if not(sabnzbd_basepath.endswith('/')):
                sabnzbd_basepath += "/"

            url = 'http%s://%s:%s%sapi?output=json&apikey=%s%s' % (ssl, host, port, sabnzbd_basepath, apikey, link)
            self.logger.debug("Sending NZB to: %s: " % url)
            return loads(urlopen(url, timeout=10).read())
        except:
            self.logger.error("Cannot contact sabnzbd")
            return

    #Future use...use staticvars
    @cherrypy.expose()
    def GetClients(self):
        nzbclients = ''
        if pytunes.settings.get('nzbget_enable', ''):
            nzbclients += '<option id="nzbget">NZBget</option>'
        if pytunes.settings.get('sabnzbd_enable', ''):
            nzbclients += '<option id="sabnzbd">Sabnzbd+</option>'
        if not nzbclients:
            nzbclients = '<option>No Clients Enabled</option>'
        return nzbclients

