#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Class for handling settings and generating settings page """
import os
import cherrypy
import pytunes
import logging
from sqlobject import connectionForURI, sqlhub, SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol, IntCol, BoolCol
from random import randrange
from socket import gethostname
from pprint import pprint
from time import gmtime, mktime
from os.path import exists, join
from cherrypy.lib.auth2 import require, member_of
import shutil

try:
    from OpenSSL import crypto
    from certgen import * # yes yes, I know, I'm lazy
except Exception as e:
    print 'Import error %s' % e

class NewznabServers(SQLObject):
    """ SQLObject class for newznab_servers table """
    name = StringCol()
    host = StringCol()
    apikey = StringCol()
    ssl = StringCol(default=None)


class Setting(SQLObject):
    """ Class for generating settings database table """
    key = StringCol()
    val = StringCol()

class XbmcServers(SQLObject):
    """ SQLObject class for xbmc_servers table """
    name = StringCol()
    host = StringCol()
    port = IntCol()
    username = StringCol(default=None)
    password = StringCol(default=None)
    mac = StringCol(default=None)

class Settings:
    """ Main class """

    def __init__(self):
        """ Create tables on load if tables don't exist """
        self.logger = logging.getLogger('pytunes.settings')
        self.logger.debug('Connecting to database: ' + pytunes.DB)
        sqlhub.processConnection = connectionForURI('sqlite:' + pytunes.DB)
        Setting.createTable(ifNotExists=True)
        NewznabServers.createTable(ifNotExists=True)
        XbmcServers.createTable(ifNotExists=True)
        self.changenewzserver(self.get('newznab_current_server', 0))
        self.changexbmcserver(self.get('xbmc_current_server', 0))

    @cherrypy.expose()
    @require(member_of("admin")) 
    def index(self, **kwargs):
        """ Set keys if settings are received. Show settings page """
        if kwargs:
            if 'enable_ssl' in kwargs:
                if kwargs['enable_ssl'] == 'on' and kwargs['app_ssl_cert'] and kwargs['app_ssl_key']:
                    self.create_certs(kwargs['app_ssl_cert'], kwargs['app_ssl_key'])
            for key, val in kwargs.items():
                self.set(key, val)
        return pytunes.LOOKUP.get_template('settings.html').render(scriptname='settings', pytunes=pytunes)

    def get(self, key, defval=''):
        """ Get a setting from the database """
        try:
            val = Setting.selectBy(key=key).getOne().val
            if val == 'on':
                return True
            elif val == "0":
                return False
            return val
        except SQLObjectNotFound:
            self.logger.debug("Unable to find the selected object: " + key)
            return defval

    def set(self, key, val):
        """ Save a setting to the database """
        self.logger.debug("Saving settings to the database.")
        try:
            setting = Setting.selectBy(key=key).getOne()
            setting.val = val
        except SQLObjectNotFound:
            Setting(key=key, val=val)

    def get_templates(self):
        """ Get a list of available templates """
        templates = []
        for template in os.listdir(os.path.join(pytunes.RUNDIR, "interfaces/")):
            current = bool(template == self.get('app_template', 'default'))
            templates.append({'name': template, 'value': template,
                'selected': current})
        return templates

    def get_themes(self):
        """ Get a list of available themes """
        path = os.path.join(pytunes.TEMPLATE, "css/themes/")
        themes = []
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        for theme in dirs:
            current = bool(theme == self.get('app_theme', 'default'))
            themes.append({'name': theme, 'value': theme, 'selected': current})
        return themes

    def create_certs(self, key_file, cert_file):
        cert_dir = os.path.join(pytunes.RUNDIR, "userdata/")
        """
        If key_file and cert_file don't exist in cert_dir, create a new
        self-signed cert and keypair and write them into that directory.
        """

        if not exists(join(cert_dir, cert_file)) \
            or not exists(join(cert_dir, key_file)):
            
            cakey = createKeyPair(TYPE_RSA, 1024)
            careq = createCertRequest(cakey, CN=gethostname())
            cacert = createCertificate(careq, (careq, cakey), 0, (0, 60*60*24*365*10)) # 10 years
            open(join(cert_dir, key_file), 'w').write(crypto.dump_privatekey(crypto.FILETYPE_PEM, cakey))
            open(join(cert_dir, cert_file), 'w').write(crypto.dump_certificate(crypto.FILETYPE_PEM, cacert))

    @cherrypy.expose()
    @require(member_of("admin")) 
    @cherrypy.tools.json_out()
    def delete_cache(self):
        try:
            cache_folder = os.path.join(pytunes.DATADIR, 'images/')
            if os.path.exists(cache_folder):
                self.logger.info('Cache folder was deleted')
                shutil.rmtree(cache_folder)
                return {'success': 'true'}
            return {'failed': 'cache folder does not exist'}
        except Exception as e:
            self.logger.error('Failed to delete cache folder ', e)
            return {'failed': e}



    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetNewzServers(self, id=None, selected=True):
        if id:
            """ Get Newznab servers info """
            try:
                server = NewznabServers.selectBy(id=id).getOne()
                print server
                return dict((c, getattr(server, c)) for c in server.sqlmeta.columns)
            except SQLObjectNotFound:
                return

        """ Get a list of all servers and the current server """
        servers = ''
        option = "<option value='%s'%s>%s</option>"
        for s in NewznabServers.select():
            print 'default', self.get('newznab_current_server')
            if selected == True and (self.get('newznab_current_server') == str(s.id)):
                servers += option % (s.id, ' selected',s.name)
            else:
                servers += option % (s.id, '',s.name)
            #servers.append({'id': s.id, 'name': s.name})
        if len(servers) < 1:
            return "<option value='None'>No Servers Registered</option>"
        #print servers
        return servers

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def setnewzserver(self, newznab_server_id, newznab_server_name, newznab_server_host, newznab_server_apikey, newznab_server_ssl=False):
        """ Create a server if id=0, else update a server """
        if newznab_server_id == "0":
            self.logger.debug("Creating Newznab-Server in database")
            try:
                new = NewznabServers(name=newznab_server_name,
                        host=newznab_server_host,
                        apikey=newznab_server_apikey,
                        ssl=newznab_server_ssl)
                #self.changenewzserver(str(new.id))
                return 1
            except Exception, e:
                self.logger.debug("Exception: " + str(e))
                self.logger.error("Unable to create Newznab-Server in database: " + str(e))
                return 0
        else:
            self.logger.debug("Updating Newznab-Server " + newznab_server_name + " in database")
            try:
                server = NewznabServers.selectBy(id=int(newznab_server_id)).getOne()
                server.name = newznab_server_name
                server.host = newznab_server_host
                server.apikey = newznab_server_apikey
                server.ssl = newznab_server_ssl
                return 1
            except SQLObjectNotFound, e:
                self.logger.error("Unable to update Newznab Server " + server.name + " in database: " + e)
                return 0

    @cherrypy.expose()
    def delnewzserver(self, id):
        """ Delete a server """
        self.logger.debug("Deleting Newznab server: %s " % str(id))
        NewznabServers.delete(id)
        self.changenewzserver()
        return

    #for the future
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def changenewzclient(self, id=0):
        try:
            #self.current_newznab_client = NewznabServers.selectBy(id=id).getOne()
            self.set('default_nzb_id', str(id))
            self.logger.info("Setting default Newznab client: " + id)
            return "success"
        except :
            self.logger.error("Failed Newznab client.")
            return "success"


    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def changenewzserver(self, id='0'):
        try:
            self.current_newznab = NewznabServers.selectBy(id=int(id)).getOne()
            self.set('newznab_current_server', id)
            self.logger.info("Selecting Newznab server: " + id)
            return "success"
        except SQLObjectNotFound:
            try:
                self.current_newznab = NewznabServers.selectBy(id=self.get('newznab_current_server')).getOne()
                self.set('newznab_current_server', str(self.current_newznab.id))
                self.logger.error("Invalid Newznab server. Selecting Default Server.")
                return "success"
            except SQLObjectNotFound:
                self.current_newznab = None
                self.logger.warning("No configured Newznab-Servers.")
                return "No valid servers"

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def getxbmcserver(self, id=None):
        if id:
            """ Get XBMC server info """
            try:
                server = XbmcServers.selectBy(id=id).getOne()
                return dict((c, getattr(server, c)) for c in server.sqlmeta.columns)
            except SQLObjectNotFound:
                return

        """ Get a list of all servers and the current server """
        servers = []
        for s in XbmcServers.select():
            servers.append({'id': s.id, 'name': s.name})
        if len(servers) < 1:
            return
        try:
            current = self.current_xbmc.name
        except AttributeError:
            current = None
        return {'current': current, 'servers': servers}

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def setxbmcserver(self, xbmc_server_id, xbmc_server_name, xbmc_server_host, xbmc_server_port,
            xbmc_server_username=None, xbmc_server_password=None, xbmc_server_mac=None):
        """ Create a server if id=0, else update a server """
        if xbmc_server_id == "0":
            self.logger.debug("Creating XBMC-Server in database")
            try:
                new = XbmcServers(name=xbmc_server_name,
                        host=xbmc_server_host,
                        port=int(xbmc_server_port),
                        username=xbmc_server_username,
                        password=xbmc_server_password,
                        mac=xbmc_server_mac)
                self.changexbmcserver(str(new.id))
                return 1
            except Exception, e:
                self.logger.debug("Exception: " + str(e))
                self.logger.error("Unable to create XBMC-Server in database:" + str(e))
                return 0
        else:
            self.logger.debug("Updating XBMC-Server " + xbmc_server_name + " in database")
            try:
                server = XbmcServers.selectBy(id=xbmc_server_id).getOne()
                server.name = xbmc_server_name
                server.host = xbmc_server_host
                server.port = int(xbmc_server_port)
                server.username = xbmc_server_username
                server.password = xbmc_server_password
                server.mac = xbmc_server_mac
                return 1
            except SQLObjectNotFound, e:
                self.logger.error("Unable to update XBMC-Server " + server.name + " in database")
                return 0

    @cherrypy.expose()
    def delxbmcserver(self, id):
        """ Delete a server """
        self.logger.debug("Deleting server " + str(id))
        XbmcServers.delete(id)
        self.changexbmcserver()
        return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def changexbmcserver(self, id=0):
        try:
            self.current_xbmc = XbmcServers.selectBy(id=id).getOne()
            self.set('xbmc_current_server', id)
            self.logger.info("Selecting XBMC server: " + id)
            return "success"
        except SQLObjectNotFound:
            try:
                self.current_xbmc = XbmcServers.select(limit=1).getOne()
                self.logger.error("Invalid server. Selecting first Available.")
                return "success"
            except SQLObjectNotFound:
                self.current_xbmc = None
                self.logger.warning("No configured XBMC-Servers.")
                return "No valid servers"

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def get_current_newznab_host(self):
        #print 'current: ', self.current
        return NewznabServers.selectBy(id=self.get('newznab_current_server', 0)).getOne()

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def get_current_xbmc(self):
        return XbmcServers.selectBy(id=self.get('xbmc_current_server', 0)).getOne()

