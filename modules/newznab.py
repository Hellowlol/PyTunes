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
            'name': 'NZB Search',
            'id': 'newznab',
            'fields': [
                {'type':'bool', 'label':'Enable', 'name':'newznab_enable'},
                {'type':'text', 'label':'Menu name', 'name':'newznab_name', 'placeholder':'NZB Search'},
                {'type':'text', 'label':'Host', 'name':'newznab_host'},
                {'type':'text', 'label':'Apikey', 'name':'newznab_apikey'},
                {'type':'bool', 'label':'Use SSL', 'name':'newznab_ssl'},
                {'type':'text', 'label':'Console Category', 'name':'newznab_console', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Movies Category', 'name':'newznab_movies', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Audio Category', 'name':'newznab_audio', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'PC Category', 'name':'newznab_pc', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'TV Category', 'name':'newznab_tv', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'XXX Category', 'name':'newznab_xxx', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Books Category', 'name':'newznab_books', 'desc':'From Sabnzbd Configuration'},
                {'type':'text', 'label':'Other Category', 'name':'newznab_other', 'desc':'From Sabnzbd Configuration'}
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

            url = 'http' + ssl + '://' + host + '/covers/tv/' + url[6:] + '.jpg'

        return get_image(url, h, w, o)

    @cherrypy.expose()
    def getcategories(self, **kwargs):
        self.logger.debug("Fetching available categories")
        try:
            settings = pytunes.settings
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
            self.logger.error("Unable to fetch categories from: %s" % url)
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
            cat = '&cat=' + cat
        res = self.fetch('search&q=' + quote(q) + cat + '&extended=1')
        link = "<a href='/sabnzbd/AddNzbFromUrl?nzb_url=%s&nzb_category=%s' class='ajax-link' title='Send To Sabnzbd+' cat='%s'><i class='icon-download-alt'></i></a>"
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


    def fetch(self, cmd):
        try:
            settings = pytunes.settings
            host = settings.get('newznab_host', '').replace('http://', '').replace('https://', '')
            ssl = 's' if settings.get('newznab_ssl', 0) else ''
            apikey = settings.get('newznab_apikey', '')
            url = 'http' + ssl + '://' + host + '/api?o=json&apikey=' + apikey + '&t=' + cmd
            self.logger.debug("Fetching information from: %s" % url)
            return loads(urlopen(url, timeout=10).read())
        except:
            self.logger.error("Unable to fetch information from: %s" % url)
            return