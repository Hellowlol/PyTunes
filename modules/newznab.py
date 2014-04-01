import cherrypy
import htpc
import math
from htpc.proxy import get_image
from urllib2 import urlopen, quote
from json import loads
import logging


class Newznab:
    def __init__(self):
        self.logger = logging.getLogger('modules.newznab')
        htpc.MODULES.append({
            'name': 'NZB Search',
            'id': 'newznab',
            'fields': [
                {'type':'bool', 'label':'Enable', 'name':'newznab_enable'},
                {'type':'text', 'label':'Menu name', 'name':'newznab_name', 'placeholder':'NZB Search'},
                {'type':'text', 'label':'Host', 'name':'newznab_host'},
                {'type':'text', 'label':'Apikey', 'name':'newznab_apikey'},
                {'type':'bool', 'label':'Use SSL', 'name':'newznab_ssl'},
                {'type':'text', 'label':'Sab Movies Category', 'name':'newznab_movies', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Sab TV Category', 'name':'newznab_tv', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Sab Music Category', 'name':'newznab_music', 'desc':'From Sabnzbd Configuration'}
        ]})

    @cherrypy.expose()
    def index(self, query='', **kwargs):
        return htpc.LOOKUP.get_template('newznab.html').render(query=query, scriptname='newznab')

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
            settings = htpc.settings
            host = settings.get('newznab_host', '').replace('http://', '').replace('https://', '')
            ssl = 's' if settings.get('newznab_ssl', 0) else ''

            url = 'http' + ssl + '://' + host + '/covers/tv/' + url[6:] + '.jpg'

        return get_image(url, h, w, o)

    @cherrypy.expose()
    def getcategories(self, **kwargs):
        self.logger.debug("Fetching available categories")
        try:
            settings = htpc.settings
            host = settings.get('newznab_host', '').replace('http://', '').replace('https://', '')
            ssl = 's' if settings.get('newznab_ssl', 0) else ''
            apikey = settings.get('newznab_apikey', '')
            url = 'http' + ssl + '://' + host + '/api?t=caps&o=xml'
            self.logger.debug("Fetching Cat information from: " + url)
            caps = urlopen(url, timeout=10).read()
            lines = caps.split('\n')
            ret = ''
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
                    name = main_name + ' > ' + subcat[1].split('"')[1]
                    ret += opt_line % (id, name)
        except:
            self.logger.error("Unable to fetch categories from: " + url)
        return ret

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def search(self, q='', cat='', **kwargs):
        ret = ''
        row = '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
        settings = htpc.settings
        sab_cat = {
            '1000':'',
            '2000':settings.get('newznab_movies', ''),
            '3000':settings.get('newznab_music', ''),
            '4000':'',
            '5000':settings.get('newznab_tv', ''),
            '6000':'',
            '7000':'',
            '8000':''
        }        
        if cat:
            cat = '&cat=' + cat
        res = self.fetch('search&q=' + quote(q) + cat + '&extended=1')
        link = "<a href='/sabnzbd/AddNzbFromUrl?nzb_url=%s&nzb_category=%s' class='ajax-confirm' title='Send To Sabnzbd+'><i class='icon-download-alt'></i></a>"
        try:
            results = res['channel']['item']
        except:
            results = res
        for each in results:
            files = str(each['attr'][4]['@attributes']['value'])
            grabs = str(each['attr'][6]['@attributes']['value'])
            category = each['category']
            title = each['title']
            num = int(each['enclosure']['@attributes']['length'])
            for x in [' bytes',' KB',' MB',' GB']:
                if num < 1024.0:
                    size = "%3.2f%s" % (num, x)
                    break
                num /= 1024.0
            dl = link % (quote(each['link']), sab_cat[str(each['attr'][0]['@attributes']['value'])])
            ret += row % (title, category, size, files, grabs, dl)
        return ret

    def fetch(self, cmd):
        try:
            settings = htpc.settings
            host = settings.get('newznab_host', '').replace('http://', '').replace('https://', '')
            ssl = 's' if settings.get('newznab_ssl', 0) else ''
            apikey = settings.get('newznab_apikey', '')
            url = 'http' + ssl + '://' + host + '/api?o=json&apikey=' + apikey + '&t=' + cmd
            self.logger.debug("Fetching information from: " + url)
            return loads(urlopen(url, timeout=10).read())
        except:
            self.logger.error("Unable to fetch information from: " + url)
            return
