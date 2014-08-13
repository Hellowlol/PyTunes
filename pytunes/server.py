#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Initiate the HTTP server according to settings """
import os
import sys
import cherrypy
import pytunes
import logging
from pytunes.manageusers import Manageusers
from sqlobject import SQLObjectNotFound
from cherrypy.lib.auth2 import AuthController, require, member_of
from cherrypy.process.plugins import Daemonizer, PIDFile


def start():
    """ Main function for starting PyTunes server """
    logger = logging.getLogger('pytunes.server')
    logger.debug("Setting up to start cherrypy")
    ssl = ''
    secure = ''
    
    # Enable auth if username and pass is set, add to db as admin
    if pytunes.USERNAME and pytunes.PASSWORD:
        logger.info("Enabling Auth for user control")
        """ Lets see if the that username and password is already in the db"""
        try:
            user = Manageusers.selectBy(username=pytunes.USERNAME).getOne()
        except SQLObjectNotFound:
            Manageusers(username=pytunes.USERNAME, password=pytunes.PASSWORD, role='admin')
        logger.debug('Updating cherrypy config, activing sessions and auth')
        cherrypy.config.update({
            'tools.sessions.on': True,
            'tools.auth.on': True,
            'tools.sessions.timeout':60
        })
    

    # Set server ip, port and root
    cherrypy.config.update({
        'server.socket_host': pytunes.HOST,
        'server.socket_port': pytunes.PORT,
        'log.screen': False,
        'server.thread_pool': 15,
        'server.socket_queue_size': 10
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
            'tools.gzip.mime_types': ['text/html', 'text/plain', 'text/css', 'text/javascript', 'application/json', 'application/javascript']
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

    # Start the CherryPy server (remove trailing slash from webdir)
    logger.info("Starting up webserver")
    print '******************************************************'
    print 'Starting Pytunes on ' + secure + 'Port ' + str(pytunes.PORT) + '.'
    print 'Start your browser and go to http' + ssl + '://localhost:' + str(pytunes.PORT) + '/' + pytunes.WEBDIR[:-1]
    print '******************************************************'
    cherrypy.quickstart(pytunes.ROOT, pytunes.WEBDIR[:-1], config=app_config)
