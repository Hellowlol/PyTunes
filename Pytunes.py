#!/usr/bin/env python
# -*- coding: utf-8 -*-A
"""
This is the main executable of PyTunes. It parses the
command line arguments, sets globals variables and calls the
start function to start the server.
"""
import os
import inspect
import sys
import htpc
import webbrowser


def parse_arguments():
    """ Get variables from commandline """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--datadir', default=None,
                        help='Set the datadirectory')
    parser.add_argument('--db', default=None,
                        help='Use a custom database')
    parser.add_argument('--host', default=None,
                        help='Use a specific host/IP')
    parser.add_argument('--port', type=int,
                        help='Use a specific port')
    parser.add_argument('--noshell', action='store_true', default=False,
                        help='Set this if you want to disable shell access. Extra security if you open the port to the world.')
    parser.add_argument('--daemon', action='store_true', default=False,
                        help='Daemonize process')
    parser.add_argument('--nobrowser', action='store_true', default=False,
                        help='Suppress Automatic Browser at Startup')
    parser.add_argument('--pid', default=False,
                        help='Generate PID file at location')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Print debug text')
    parser.add_argument('--nopass', action='store_true', default=False,
                        help='Help with lost password')
    parser.add_argument('--webdir', default=None,
                        help='Use a custom webdir')
    parser.add_argument('--loglevel', default='info',
                        help='Set a loglevel. Allowed values: debug, info, warning, error, critical')
    return parser.parse_args()


def load_modules():
    """ Import the system modules """
    from htpc.root import Root
    htpc.ROOT = Root()
    from htpc.settings import Settings
    htpc.ROOT.settings = Settings()
    from htpc.log import Log
    htpc.ROOT.log = Log()
    from htpc.updater import Updater
    htpc.ROOT.update = Updater()
    for module in os.listdir('modules'):
        if module.endswith('.py') and not module.startswith('_'):
            __import__('modules.' + module[0:-3])
            for name, obj in inspect.getmembers(sys.modules['modules.' + module[0:-3]]):
                if inspect.isclass(obj) and name.lower() == module[0:-3]:
                    setattr(htpc.ROOT, module[0:-3], obj())

def main():
    """
    Main function is called at startup.
    """
    # Parse runtime arguments
    args = parse_arguments()

    # Set root and insert bundled libraries into path
    htpc.RUNDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    sys.path.insert(0, os.path.join(htpc.RUNDIR, 'libs'))

    # Set datadir, create if it doesn't exist and exit if it isn't writable.
    htpc.DATADIR = os.path.join(htpc.RUNDIR, 'userdata/')
    if args.datadir:
        htpc.DATADIR = args.datadir
    if not os.path.isdir(htpc.DATADIR):
        os.makedirs(htpc.DATADIR)
    if not os.access(htpc.DATADIR, os.W_OK):
        sys.exit("No write access to userdata folder")

    from mako.lookup import TemplateLookup

    # Enable debug mode if needed
    htpc.DEBUG = args.debug

    # Set loglevel
    htpc.LOGLEVEL = args.loglevel.lower()

    # Set default database and overwrite if supplied through commandline
    htpc.DB = os.path.join(htpc.DATADIR, 'database.db')
    if args.db:
        htpc.DB = args.db

    # Set browser override if supplied through commandline
    htpc.NB = args.nobrowser

    # Load settings from database
    from htpc.settings import Settings
    htpc.settings = Settings()

    # Check for SSL
    htpc.SSLCERT = htpc.settings.get('app_ssl_cert')
    htpc.SSLKEY = htpc.settings.get('app_ssl_key')

    htpc.WEBDIR = htpc.settings.get('app_webdir', '/')
    if args.webdir:
        htpc.WEBDIR = args.webdir
    if not(htpc.WEBDIR.endswith('/')):
        htpc.WEBDIR += '/'

    # Inititialize root and settings page
    load_modules()

    htpc.TEMPLATE = os.path.join(htpc.RUNDIR, 'interfaces/',
                                 htpc.settings.get('app_template', 'default'))
    htpc.LOOKUP = TemplateLookup(directories=[os.path.join(htpc.TEMPLATE, 'html/')])

    # Overwrite host setting if supplied through commandline
    htpc.HOST = htpc.settings.get('app_host', '0.0.0.0')
    if args.host:
        htpc.HOST = args.host

    # Overwrite port setting if supplied through commandline
    htpc.PORT = int(htpc.settings.get('app_port', 8085))
    if args.port:
        htpc.PORT = args.port

    #Override for lost password
    if not args.nopass:
        htpc.USERNAME = htpc.settings.get('app_username')
        htpc.PASSWORD = htpc.settings.get('app_password')    
    else:
        htpc.USERNAME = ''
        htpc.PASSWORD = ''   

    #Select if you want to disable shell commands from PyTunes
    htpc.NOSHELL = args.noshell
     
    # Select whether to run as daemon
    htpc.DAEMON = args.daemon

    # Set Application PID
    htpc.PID = args.pid

    # Start the webbrowser.....We need a way to detect whether there was a restart signal from an open browser so we don't open another.
    if htpc.settings.get('browser')  and not htpc.DEBUG and not htpc.DAEMON and not htpc.NB:
        nb_ssl = 's' if htpc.SSLCERT and htpc.SSLKEY else ''
        nb_host = 'localhost' if htpc.settings.get('app_host') == '0.0.0.0' else htpc.settings.get('app_host')
        openbrowser = 'http%s://%s:%s%s' % (nb_ssl, nb_host,  htpc.PORT, htpc.WEBDIR[:-1])
        webbrowser.open(openbrowser, new=2, autoraise=True)

    # Start the server
    from htpc.server import start
    start()


if __name__ == '__main__':
    main()
