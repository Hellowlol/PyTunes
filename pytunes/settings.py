""" Class for handling settings and generating settings page """
import os
import cherrypy
import pytunes
import logging
from sqlobject import connectionForURI, sqlhub, SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol
from random import randrange
from OpenSSL import crypto, SSL
from socket import gethostname
from pprint import pprint
from time import gmtime, mktime
from os.path import exists, join


class Setting(SQLObject):
    """ Class for generating settings database table """
    key = StringCol()
    val = StringCol()


class Settings:
    """ Main class """

    def __init__(self):
        """ Create table on load if table doesnt exist """
        self.logger = logging.getLogger('pytunes.settings')
        self.logger.debug('Connecting to database: ' + pytunes.DB)
        sqlhub.processConnection = connectionForURI('sqlite:' + pytunes.DB)
        Setting.createTable(ifNotExists=True)

    @cherrypy.expose()
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
        """
        If key_file and cert_file don't exist in cert_dir, create a new
        self-signed cert and keypair and write them into that directory.
        """
        cert_dir = os.path.join(pytunes.RUNDIR, "userdata/")

        if not exists(join(cert_dir, cert_file)) \
                or not exists(join(cert_dir, key_file)):
            
            # create a key pair
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 1024)

            # create a self-signed cert
            cert = crypto.X509()
            cert.get_subject().C = "RU"
            cert.get_subject().ST = "My State"
            cert.get_subject().L = "My Town"
            cert.get_subject().O = "my company"
            cert.get_subject().OU = "my organization"
            cert.get_subject().CN = gethostname()
            cert.set_serial_number(randrange(1000000000))
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10*365*24*60*60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.sign(k, 'sha1')

            open(join(cert_dir, cert_file), "wt").write(
                crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            open(join(cert_dir, key_file), "wt").write(
                crypto.dump_privatekey(crypto.FILETYPE_PEM, k))


