import cherrypy
import pytunes
import math
from pytunes.proxy import get_image
from urllib2 import urlopen, quote
from json import loads
from sqlobject import SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol, IntCol, BoolCol
import logging


class NewznabServers(SQLObject):
    """ SQLObject class for newznab_servers table """
    name = StringCol()
    host = StringCol()
    apikey = StringCol()
    username = StringCol(default=None)
    password = StringCol(default=None)
    ssl = BoolCol(default=False)

class Newznab:
    def __init__(self):
        self.logger = logging.getLogger('modules.newznab')
        NewznabServers.createTable(ifNotExists=True)
        pytunes.MODULES.append({
            'name': 'NZB Search',
            'id': 'newznab',
            'fields': [
                {'type':'bool', 'label':'Enable', 'name':'newznab_enable'},
                {'type':'text', 'label':'Menu name', 'name':'newznab_name', 'placeholder':''},
                {'type':'select',
                 'label':'Default NZB Client',
                 'name':'default_nzb_id',
                 'options':[],
                    'desc':'Only Enabled Clients Will Show' 
                },
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
            'action': pytunes.WEBDIR + 'newznab/setserver',
            #'test': pytunes.WEBDIR + 'newznab/ping',
            'fields': [
                {'type':'select',
                 'label':'Server',
                 'name':'newznab_server_id',
                 'options':[
                    {'name':'New', 'value':0}
                ]},
                {'type':'text',
                 'label':'Name',
                 'name':'newznab_server_name'},
                {'type':'text', 'label':'Host', 'name':'newznab_server_host'},
                {'type':'text', 'label':'Apikey', 'name':'newznab_server_apikey'},
                {'type':'text',
                 'label':'Username',
                 'name':'newznab_server_username'},
                {'type':'password',
                 'label':'Password',
                 'name':'newznab_server_password'},
                {'type':'bool', 'label':'Use SSL', 'name':'newznab_server_ssl'}
        ]})
        server = pytunes.settings.get('newznab_current_server', 0)
        self.changeserver(server)

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
    @cherrypy.tools.json_out()
    def getserver(self, id=None):
        if id:
            """ Get XBMC server info """
            try:
                server = NewznabServers.selectBy(id=id).getOne()
                return dict((c, getattr(server, c)) for c in server.sqlmeta.columns)
            except SQLObjectNotFound:
                return

        """ Get a list of all servers and the current server """
        servers = []
        for s in NewznabServers.select():
            servers.append({'id': s.id, 'name': s.name})
        if len(servers) < 1:
            return
        try:
            current = self.current.name
        except AttributeError:
            current = None
        return {'current': current, 'servers': servers}

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def setserver(self, newznab_server_id, newznab_server_name, newznab_server_host,
            newznab_server_username=None, newznab_server_password=None, newznab_server_ssl=False):
        """ Create a server if id=0, else update a server """
        if newznab_server_id == "0":
            self.logger.debug("Creating Newznab-Server in database")
            try:
                id = NewznabServers(name=newznab_server_name,
                        host=newznab_server_host,
                        apikey=newznab_server_apikey,
                        username=newznab_server_username,
                        password=newznab_server_password,
                        ssl=newznab_server_ssl)
                self.setcurrent(id)
                return 1
            except Exception, e:
                self.logger.debug("Exception: " + str(e))
                self.logger.error("Unable to create Newznab-Server in database")
                return 0
        else:
            self.logger.debug("Updating Newznab-Server " + newznab_server_name + " in database")
            try:
                server = NewznabServers.selectBy(id=newznab_server_id).getOne()
                server.name = newznab_server_name
                server.host = newznab_server_host
                server.apikey = newznab_server_apikey
                server.username = newznab_server_username
                server.password = newznab_server_password
                server.ssl = newznab_server_ssl
                return 1
            except SQLObjectNotFound, e:
                self.logger.error("Unable to update XBMC-Server " + server.name + " in database")
                return 0

    @cherrypy.expose()
    def delserver(self, id):
        """ Delete a server """
        self.logger.debug("Deleting Newznab server " + str(id))
        NewznabServers.delete(id)
        self.changeserver()
        return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def changeserver(self, id=0):
        try:
            self.current = NewznabServers.selectBy(id=id).getOne()
            pytunes.settings.set('newznab_current_server', id)
            self.logger.info("Selecting Newznab server: " + id)
            return "success"
        except SQLObjectNotFound:
            try:
                self.current = NewznabServers.select(limit=1).getOne()
                self.logger.error("Invalid Newzbab server. Selecting first Available.")
                return "success"
            except SQLObjectNotFound:
                self.current = None
                self.logger.warning("No configured Newznab-Servers.")
                return "No valid servers"

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
