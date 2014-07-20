#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Initiate the HTTP server according to settings """
import os
import sys
import cherrypy
import pytunes
import logging
from cherrypy.lib.auth2 import AuthController, require, member_of, name_is
from cherrypy.process.plugins import Daemonizer, PIDFile
#from cherrypy.lib.auth_digest import get_ha1_dict_plain


def start():
    """ Main function for starting PyTunes server """
    logger = logging.getLogger('pytunes.server')
    logger.debug("Setting up to start cherrypy")
    ssl = ''
    secure = ''

    # Set server ip, port and root
    cherrypy.config.update({
        'server.socket_host': pytunes.HOST,
        'server.socket_port': pytunes.PORT,
        'log.screen': False
    })

    # Set server environment to production unless when debugging
    if not pytunes.DEBUG:
        cherrypy.config.update({
            'environment': 'production'
        })

    # Enable SSL
    if pytunes.SSLCERT and pytunes.SSLKEY:
        #cert_dir = os.path.join(pytunes.RUNDIR, "userdata/")
        print os.path.join(pytunes.RUNDIR, "userdata/", pytunes.SSLCERT)
        ssl = 's'
        secure = 'Secure '
        cherrypy.config.update({
            'server.ssl_module': 'builtin',
            'server.ssl_certificate': os.path.join(pytunes.RUNDIR, "userdata/", pytunes.SSLCERT),
            'server.ssl_private_key': os.path.join(pytunes.RUNDIR, "userdata/", pytunes.SSLKEY)
        })

    # Daemonize cherrypy if specified
    if pytunes.DAEMON:
        if sys.platform == 'win32':
            logger.error("You are using Windows - I cannot setup daemon mode. Please use the pythonw executable instead.")
            logger.error("More information at http://docs.python.org/2/using/windows.html.")
        else:
            Daemonizer(cherrypy.engine).subscribe()

    # Create PID if specified
    if pytunes.PID:
        PIDFile(cherrypy.engine, pytunes.PID).subscribe()

    # Set static directories
    webdir = os.path.join(pytunes.RUNDIR, pytunes.TEMPLATE)
    favicon = os.path.join(webdir, "img/favicon.ico")
    app_config = {
        '/': {
            'tools.staticdir.root': webdir,
            'tools.encode.on': True,
            'tools.encode.encoding': 'utf-8',
            'tools.gzip.on': True,
            'tools.sessions.on': True,
            'tools.auth.on': True
        },
        '/js': {
            'tools.caching.on': True,
            'tools.caching.force': True,
            'tools.caching.delay': 0,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 6,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'js'
        },
        '/css': {
            'tools.caching.on': True,
            'tools.caching.force': True,
            'tools.caching.delay': 0,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 6,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'css'
        },
        '/img': {
            'tools.caching.on': True,
            'tools.caching.force': True,
            'tools.caching.delay': 0,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 6,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'img'
        },
        '/favicon.ico': {
            'tools.caching.on': True,
            'tools.caching.force': True,
            'tools.caching.delay': 0,
            'tools.expires.on': True,
            'tools.expires.secs': 60 * 60 * 6,
            'tools.staticfile.on': True,
            'tools.staticfile.filename': favicon
        },
    }

    auth = AuthController()
    
    #restricted = RestrictedArea()
    # Require username and password if they are set
    if pytunes.USERNAME and pytunes.PASSWORD:
        logger.info("Enabling username/password access")
        userpassdict = {pytunes.USERNAME: pytunes.PASSWORD}
        get_ha1 = get_ha1_dict_plain(userpassdict)
        app_config['/'].update({
            'tools.auth_digest.on': True,
            'tools.auth_digest.realm': "PyTunes",
            'tools.auth_digest.get_ha1': get_ha1,
            'tools.auth_digest.key': 'a565c27146791cfb'
        })

    # Start the CherryPy server (remove trailing slash from webdir)
    logger.info("Starting up webserver")
    print '******************************************************'
    print 'Starting Pytunes on ' + secure + 'Port ' + str(pytunes.PORT) + '.'
    print 'Start your browser and go to http' + ssl + '://localhost:' + str(pytunes.PORT) + '/' + pytunes.WEBDIR[:-1]
    print '******************************************************'
    cherrypy.quickstart(pytunes.ROOT, pytunes.WEBDIR[:-1], config=app_config)
