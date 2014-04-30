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
import pytunes
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
    from pytunes.root import Root
    pytunes.ROOT = Root()
    from pytunes.settings import Settings
    pytunes.ROOT.settings = Settings()
    from pytunes.log import Log
    pytunes.ROOT.log = Log()
    from pytunes.updater import Updater
    pytunes.ROOT.update = Updater()
    for module in os.listdir('modules'):
        if module.endswith('.py') and not module.startswith('_'):
            __import__('modules.' + module[0:-3])
            for name, obj in inspect.getmembers(sys.modules['modules.' + module[0:-3]]):
                if inspect.isclass(obj) and name.lower() == module[0:-3]:
                    setattr(pytunes.ROOT, module[0:-3], obj())

def main():
    """
    Main function is called at startup.
    """
    # Parse runtime arguments
    args = parse_arguments()

    # Set root and insert bundled libraries into path
    pytunes.RUNDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
    sys.path.insert(0, os.path.join(pytunes.RUNDIR, 'libs'))

    # Set datadir, create if it doesn't exist and exit if it isn't writable.
    pytunes.DATADIR = os.path.join(pytunes.RUNDIR, 'userdata/')
    if args.datadir:
        pytunes.DATADIR = args.datadir
    if not os.path.isdir(pytunes.DATADIR):
        os.makedirs(pytunes.DATADIR)
    if not os.access(pytunes.DATADIR, os.W_OK):
        sys.exit("No write access to userdata folder")

    from mako.lookup import TemplateLookup

    # Enable debug mode if needed
    pytunes.DEBUG = args.debug

    # Set loglevel
    pytunes.LOGLEVEL = args.loglevel.lower()

    # Set default database and overwrite if supplied through commandline
    pytunes.DB = os.path.join(pytunes.DATADIR, 'database.db')
    if args.db:
        pytunes.DB = args.db

    # Set browser override if supplied through commandline
    pytunes.NOBROWSER = args.nobrowser

    # Load settings from database
    from pytunes.settings import Settings
    pytunes.settings = Settings()

    # Check for SSL
    pytunes.SSLCERT = pytunes.settings.get('app_ssl_cert')
    pytunes.SSLKEY = pytunes.settings.get('app_ssl_key')

    pytunes.WEBDIR = pytunes.settings.get('app_webdir', '/')
    if args.webdir:
        pytunes.WEBDIR = args.webdir
    if not(pytunes.WEBDIR.endswith('/')):
        pytunes.WEBDIR += '/'

    # Inititialize root and settings page
    load_modules()

    pytunes.TEMPLATE = os.path.join(pytunes.RUNDIR, 'interfaces/',
                                 pytunes.settings.get('app_template', 'default'))
    pytunes.LOOKUP = TemplateLookup(directories=[os.path.join(pytunes.TEMPLATE, 'html/')])

    # Overwrite host setting if supplied through commandline
    pytunes.HOST = pytunes.settings.get('app_host', '0.0.0.0')
    if args.host:
        pytunes.HOST = args.host

    # Overwrite port setting if supplied through commandline
    pytunes.PORT = int(pytunes.settings.get('app_port', 8085))
    if args.port:
        pytunes.PORT = args.port

    #Override for lost password
    if not args.nopass:
        pytunes.USERNAME = pytunes.settings.get('app_username')
        pytunes.PASSWORD = pytunes.settings.get('app_password')    
    else:
        pytunes.USERNAME = ''
        pytunes.PASSWORD = ''   

    #Select if you want to disable shell commands from PyTunes
    pytunes.NOSHELL = args.noshell
     
    # Select whether to run as daemon
    pytunes.DAEMON = args.daemon

    # Set Application PID
    pytunes.PID = args.pid

    # Start the webbrowser.....We need a way to detect whether there was a restart signal from an open browser so we don't open another.
    if pytunes.settings.get('browser')  and not pytunes.DEBUG and not pytunes.DAEMON and not pytunes.NOBROWSER:
        nb_ssl = 's' if pytunes.SSLCERT and pytunes.SSLKEY else ''
        nb_host = 'localhost' if pytunes.settings.get('app_host') == '0.0.0.0' else pytunes.settings.get('app_host')
        openbrowser = 'http%s://%s:%s%s' % (nb_ssl, nb_host,  pytunes.PORT, pytunes.WEBDIR[:-1])
        webbrowser.open(openbrowser, new=2, autoraise=True)

    # Start the server
    from pytunes.server import start
    start()


if __name__ == '__main__':
    main()
