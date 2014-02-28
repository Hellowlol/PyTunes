import cherrypy
import htpc
from htpc.proxy import get_image
from urllib2 import urlopen, quote
from json import loads
import logging
import xml.etree.ElementTree as xml
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def getcategories(self, **kwargs):
        self.logger.debug("Fetching available categories")
        return self.fetch('caps')['categories']

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def search(self, q='', cat='', **kwargs):
        if cat:
            cat = '&cat=' + cat
        result = self.fetch('search&q=' + quote(q) + cat + '&extended=1')
        try:
            return result['channel']['item']
        except:
            return result

    def fetch(self, cmd):
        try:
            settings = htpc.settings
            host = settings.get('tmdb_host', '').replace('http://', '').replace('https://', '')
            ssl = 's' if settings.get('tmdb_ssl', 0) else ''
            apikey = settings.get('tmdb_apikey', '')

            url = 'http' + ssl + '://' + host + '/api?o=json&apikey=' + apikey + '&t=' + cmd
            #url = 'http' + ssl + '://' + host + '/api?o=xml&apikey=' + apikey + '&t=' + cmd

            self.logger.debug("Fetching information from: " + url)
            return loads(urlopen(url, timeout=10).read())
            #return xml.parse(urlopen(url, timeout=10).read())
        except:
            self.logger.error("Unable to fetch information from: " + url)
            return
