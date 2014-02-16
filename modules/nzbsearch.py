import cherrypy
import htpc
from htpc.proxy import get_image
import urllib2
from json import loads
import logging
from jsonrpclib import Server
from sqlobject import SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol, IntCol

class NewznabServers(SQLObject):
    """ SQLObject class for newznab_servers table """
    name = StringCol()
    host = StringCol()
    apikey = StringCol()
    ssl = IntCol()

class NZBSearch:
    def __init__(self):
        self.logger = logging.getLogger('modules.search')
        NewznabServers.createTable(ifNotExists=True)
        htpc.MODULES.append({
            'name': 'Newznab',
            'id': 'newznab',
            'fields': [
                {'type':'bool', 'label':'Enable', 'name':'newznab_enable'},
                {'type':'text', 'label':'Menu name', 'name':'newznab_name'},
        ]})
        htpc.MODULES.append({
            'name': 'Newznab Servers',
            'id': 'newznab_update_server',
            'action': htpc.WEBDIR + 'nzbsearch/setserver',
            #'test': htpc.WEBDIR + 'nzbsearch/ping',
            'fields': [
                {'type':'select',
                 'label':'NZB Server',
                 'name':'newznab_server_id',
                 'options':[
                    {'name':'New', 'value':0}
                ]},
                {'type':'text', 'label':'Name', 'name':'newznab_server_name'},
                {'type':'text', 'label':'Host', 'name':'newznab_host'},
                {'type':'text', 'label':'Apikey', 'name':'newznab_apikey'},
                {'type': 'bool', 'label': 'Use SSL', 'name': 'newznab_ssl'}
        ]})
        server = htpc.settings.get('newznab_current_server', 0)
        self.changeserver(server)


    @cherrypy.expose()
    def index(self, query='', **kwargs):
        return htpc.LOOKUP.get_template('nzbsearch.html').render(query=query, scriptname='nzbsearch')

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
            """ Get Newznab server info """
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
    def setserver(self, newznab_id, newznab_name, newznab_host, newznab_apikey):
        """ Create a server if id=0, else update a server """
        if newznab_server_id == "0":
            self.logger.debug("Creating Newznab Server in database")
            try:
                id = NewznabServers(name=xbmc_server_name, host=newznab_host, apikey=newznab_apikey)
                self.setcurrent(id)
                return 1
            except Exception, e:
                self.logger.debug("Exception: " + str(e))
                self.logger.error("Unable to create Newznab Server in database")
                return 0
        else:
            self.logger.debug("Updating Newznab Server " + newznab_server_name + " in database")
            try:
                server = NewznabServers.selectBy(id=xbmc_server_id).getOne()
                server.name = newznab_server_name
                server.host = newznab_server_host
                server.apikey = newznab_server_username
                return 1
            except SQLObjectNotFound, e:
                self.logger.error("Unable to update Newznab Server " + server.name + " in database")
                return 0

    @cherrypy.expose()
    def delserver(self, id):
        """ Delete a server """
        self.logger.debug("Deleting server " + str(id))
        NewznabServers.delete(id)
        self.changeserver()
        return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def changeserver(self, id=0):
        try:
            self.current = NewznabServers.selectBy(id=id).getOne()
            htpc.settings.set('newznab_current_server', id)
            self.logger.info("Selecting Newznab server: " + id)
            return "success"
        except SQLObjectNotFound:
            try:
                self.current = NewznabServers.select(limit=1).getOne()
                self.logger.error("Invalid server. Selecting first Available.")
                return "success"
            except SQLObjectNotFound:
                self.current = None
                self.logger.warning("No configured Newznab Servers.")
                return "No valid servers"


    @cherrypy.expose()
    def thumb(self, url, h=None, w=None, o=100):
        if url.startswith('rageid'):
            settings = htpc.settings
            host = settings.get('newznab_host', '').replace('http://', '').replace('https://', '')
            ssl = 's' if settings.get('newznab_ssl', 0) else ''

            url = 'http' + ssl + '://' + host + '/covers/tv/' + url[6:] + '.jpg'

        return get_image(url, h, w, o)

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
        result = self.fetch('search&q=' + urllib2.quote(q) + cat + '&extended=1')
        try:
            return result['channel']['item']
        except:
            return result

    def fetch(self, cmd):
        try:
            settings = htpc.settings
            host = settings.get('newznab_host', '').replace('http://', '').replace('https://', '')
            ssl = 's' if settings.get('newznab_ssl', 0) else ''
            apikey = settings.get('newznab_apikey', '')
            url = 'http' + ssl + '://' + host + '/api?o=json&apikey=' + apikey + '&t=' + cmd
            self.logger.debug("Fetching information from: " + url)
            #return loads(urllib2.urlopen(url, timeout=10).read())
            #return xml.parse(urllib2.urlopen(url, timeout=10).read())
            request = urllib2.Request(url)
            request.add_header('User-agent', 'PyTunes Media Server Manager')
            try:
                resource = urllib2.urlopen(request)
                return loads(resource.read())
            except urllib2.HTTPError, err:
                self.logger.error("HTTP Error Code Received: " + str(err.code))
        except:
            self.logger.error("Unable to fetch information from: " + url)
            return
