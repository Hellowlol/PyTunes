import cherrypy
import htpc
import glob
import os
import sys
from htpc import staticvars
from htpc.proxy import get_image
from urllib2 import urlopen, quote
from json import loads
import logging
import xml.etree.ElementTree as xml
from engines import ka

class Torrents:
    def __init__(self):
        self.logger = logging.getLogger('modules.torrents')
        htpc.MODULES.append({
            'name': 'Torrent Search',
            'id': 'torrents',
            'fields': [
                {'type':'bool', 'label':'Enable', 'name':'torrents_enable'},
                {'type':'text', 'label':'Menu name', 'name':'torrents_name'},
                {'type':'text', 'label':'Seeds', 'name':'torrents_seeds', 'value':'5', 'desc':'Minimum Number of Seeders'},
        ]})

    @cherrypy.expose()
    def index(self, query='', **kwargs):
        return htpc.LOOKUP.get_template('torrents.html').render(scriptname='torrents')

    @cherrypy.expose()
    def sizeof(self, num):
        for x in ['bytes','KB','MB','GB']:
            if num < 1024.0:
                return "%3.1f%s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TB')

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def search(self, q='', cat='', **kwargs):
        ret = ''
        row = '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
        supported_engines = ['kickasstorrents']
        results =  ka.search(q, cat)
        for r in results:
            icon = "<img alt='icon' src='../img/kickasstorrents.png'/>"
            link = r['link'].split('?')[0]
            dl = "<a href='/qbittorrent/command?cmd=download&hash=%s' class='ajax-link' title='Send to qBittorrent'><i class='icon-download-alt'></a>" % link
            name = "<a href='" + r['desc_link'] + "' target='_blank'>" + r['name'] + "</a>"
            num = int(r['size'])
            for x in [' bytes',' KB',' MB',' GB']:
                if num < 1024.0:
                    size = "%3.2f%s" % (num, x)
                    break
                num /= 1024.0
            ret += row % (icon, name, size, r['seeds'], r['leech'], r['engine_url'], dl)
        return ret


