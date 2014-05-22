"""
Logging
"""
import time
import re
import stat
import os
import cherrypy
import pytunes
import logging
import logging.handlers as handlers


class Log:
    """ Root class """
    def __init__(self):
        """ Initialize the logger """
        self.logfile = os.path.join(pytunes.DATADIR, 'pytunes.log')
        pytunes.LOGGER = logging.getLogger()
        self.logch = logging.StreamHandler()
        self.logfh = handlers.TimedRotatingFileHandler(self.logfile, when='midnight', interval=1, backupCount=5)

        logformatter = logging.Formatter('%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s', "%Y-%m-%d %H:%M:%S")
        self.logch.setFormatter(logformatter)
        self.logfh.setFormatter(logformatter)

        if pytunes.LOGLEVEL == 'debug' or pytunes.DEBUG:
            loglevel = logging.DEBUG
        elif pytunes.LOGLEVEL == 'info':
            loglevel = logging.INFO
        elif pytunes.LOGLEVEL == 'warning':
            loglevel = logging.WARNING
        elif pytunes.LOGLEVEL == 'error':
            loglevel = logging.ERROR
        else:
            loglevel = logging.CRITICAL

        self.logch.setLevel(loglevel)
        self.logfh.setLevel(loglevel)
        pytunes.LOGGER.setLevel(loglevel)

        # Disable cherrypy access log
        logging.getLogger('cherrypy.access').propagate = False

        pytunes.LOGGER.addHandler(self.logch)
        pytunes.LOGGER.addHandler(self.logfh)

        pytunes.LOGGER.info("Welcome to PyTunes Media Server Manager!")
        pytunes.LOGGER.info("Loglevel set to " + pytunes.LOGLEVEL)

    @cherrypy.expose()
    def index(self):
        """ Show log """
        return pytunes.LOOKUP.get_template('log.html').render(scriptname='log')

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def getlog(self, lines=10, level=2):
        """ Get log as JSON """
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'][-int(level):]
        content = []
        try:
            for line in reversed(open(self.logfile, 'r').readlines()):
                line = line.split(' :: ')
                if len(line) > 1 and line[2] in levels:
                    content.append(line)
                    if len(content) >= int(lines):
                        break
        except IOError:
            # Can't log this error since there is no log file.
            pass

        return content

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def deletelog(self):
        try:
            open(self.logfile, 'w').close()
            return "Log file deleted"
        except Exception, e:
            return "Cannot delete log file: " + str(e)
