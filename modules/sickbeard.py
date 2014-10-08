#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import cherrypy
import pytunes
from urllib import quote
from urllib2 import urlopen
from json import loads
import logging
import cgi
from cherrypy.lib.auth2 import require

class Sickbeard:
    def __init__(self):
        self.logger = logging.getLogger('modules.sickbeard')
        pytunes.MODULES.append({
            'name': 'Sickbeard',
            'id': 'sickbeard',
            'test': '%sickbeard/ping' % pytunes.WEBDIR,
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'sickbeard_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'sickbeard_name', 'placeholder':''},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'sickbeard_host', 'placeholder':''},
                {'type': 'text', 'label': 'Port *', 'name': 'sickbeard_port', 'placeholder':'', 'desc':'Default is 8081'},
                {'type': 'text', 'label': 'Basepath', 'name': 'sickbeard_basepath'},
                {'type': 'text', 'label': 'API key', 'name': 'sickbeard_apikey'},
                {'type': 'bool', 'label': 'Use SSL', 'name': 'sickbeard_ssl'}
        ]})

    @cherrypy.expose()
    @require()
    def index(self, query=''):
        return pytunes.LOOKUP.get_template('sickbeard.html').render(scriptname='sickbeard', query=query)

    @cherrypy.expose()
    @require()
    def view(self, tvdbid):
        if not (tvdbid.isdigit()):
            raise cherrypy.HTTPError("500 Error", "Invalid show ID.")
            self.logger.error("Invalid show ID was supplied: %s" % str(tvdbid))
            return False

        return pytunes.LOOKUP.get_template('sickbeard_view.html').render(scriptname='sickbeard_view', tvdbid=tvdbid)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def ping(self, sickbeard_host, sickbeard_port, sickbeard_apikey, sickbeard_basepath, sickbeard_ssl = False, **kwargs):
        ssl = 's' if sickbeard_ssl else ''
        self.logger.debug("Testing connectivity")
        try:
            if not (sickbeard_basepath.endswith('/')):
                sickbeard_basepath += "/"

            url = 'http%s://%s:%s%sapi/%s/?cmd=sb.ping' % (ssl, sickbeard_host, sickbeard_port, sickbeard_basepath, sickbeard_apikey)
            self.logger.debug("Trying to contact sickbeard via %s" % url)
            response = loads(urlopen(url, timeout=10).read())
            if response.get('result') == "success":
                self.logger.debug("Sicbeard connectivity test success")
                return response
        except:
            self.logger.error("Unable to contact sickbeard via %s" % url)
            return

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetShowList(self):
        self.logger.debug("Fetching Shows list")
        sb_table = []
        sb_table_out = []
        list = self.fetch('shows&sort=name')
        sb_row = "<tr><td><a href='/sickbeard/view/%s'>%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td title='Downloaded/Snatched/Wanted/Skipped/Ignored/Unaired/Total'>%s</td><td><div class='progress span2'><div class='bar bar-success' style='width: %s%s;' title='%s Downloaded'></div><div class='bar bar-warning' style='width: %s%s;'title='%s Snatched'></div></div></td></tr>"
        #print list
        for show in list['data']:
            showlist = {}
            showlist['show'] = show
            if show[:4] == 'The ':
                showlist['sortshow'] = show[4:]
            else:
                showlist['sortshow'] = show
            #showlist['sortshow'] = shortshow
            #print show['status']
            #print show['network']
            #print show['quality']
            showlist['nextair'] = list['data'][show]['next_ep_airdate']
            showlist['status'] = list['data'][show]['status']
            showlist['network'] = list['data'][show]['network']
            showlist['quality'] = list['data'][show]['quality']
            showlist['tvdbid'] = list['data'][show]['tvdbid']
            sdata = self.fetch('show.stats&tvdbid=%s' % list['data'][show]['tvdbid'])
            #print sdata
            if sdata['message']:
                print sdata['message'], show
                #log it and put error on prog bar
                continue
            showlist['downloaded'] = sdata['data']['downloaded']['total']
            showlist['snatched'] = sdata['data']['snatched']['total']
            showlist['total'] = sdata['data']['total']
            showlist['unaired'] = sdata['data']['unaired']
            showlist['wanted'] = sdata['data']['wanted']
            showlist['ignored'] = sdata['data']['ignored']
            showlist['skipped'] = sdata['data']['skipped']
            showlist['stats'] = '%s/%s/%s/%s/%s/%s/%s' % (showlist['downloaded'], showlist['snatched'], showlist['wanted'], showlist['skipped'], showlist['ignored'], showlist['unaired'], showlist['total'])
            showlist['percent_downloaded'] = 0
            showlist['percent_snatched'] = 0
            if showlist['total']:
                showlist['percent_downloaded'] = 100*(showlist['downloaded']/showlist['total'])
                showlist['percent_snatched'] = 100*(showlist['snatched']/showlist['total'])
            #print downloaded, snatched
            #print stats
            sb_table.append(showlist)
        for showrow in sorted(sb_table, key=lambda k: k['sortshow']):
            if showrow['status'] == 'Continuing':
                status = "<span class='label label-success'><i class='icon-repeat icon-white' /> %s</span>" % showrow['status']
            else: 
                status = "<span class='label label-important'><i class='icon-remove icon-white' /> %s</span>" % showrow['status']
            if showrow['quality'] in ['HD720p', 'HD TV', 'HD 1080p', 'HD']:
                quality = "<span class='label label-info'>%s</span>" % showrow['quality']
            else:
                quality = "<span class='label label-warning'>%s</span>" % showrow['quality']
            sb_table_out.append(sb_row % (showrow['tvdbid'], showrow['show'], status, showrow['nextair'], showrow['network'], quality, showrow['stats'], showrow['percent_downloaded'], '%', showrow['downloaded'], showrow['percent_snatched'], '%', showrow['snatched']))
        #print ''.join(sb_table_out)
        return ''.join(sb_table_out)
            
        #return self.fetch('shows&sort=name')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetNextAired(self):
        self.logger.debug("Fetching Next Aired Episodes")
        return self.fetch('future')

    @cherrypy.expose()
    @require()
    def GetBanner(self, tvdbid):
        self.logger.debug("Fetching Banner")
        cherrypy.response.headers['Content-Type'] = 'image/jpeg'
        return self.fetch('show.getbanner&tvdbid=%s' % tvdbid, True)

    @cherrypy.expose()
    @require()
    def GetPoster(self, tvdbid):
        self.logger.debug("Fetching Poster")
        cherrypy.response.headers['Content-Type'] = 'image/jpeg'
        return self.fetch('show.getposter&tvdbid=%s' % tvdbid, True)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetHistory(self, limit=''):
        self.logger.debug("Fetching History")
        return self.fetch('history&limit=%s' % limit)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetLogs(self):
        self.logger.debug("Fetching Logs")
        return self.fetch('logs&min_level=info')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def AddShow(self, tvdbid):
        self.logger.debug("Adding a Show")
        return self.fetch('show.addnew&tvdbid=%s' % tvdbid)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetShow(self, tvdbid):
        
        self.logger.debug("Fetching Show")
        return self.fetch('show&tvdbid=%s' % tvdbid)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def GetSeason(self, tvdbid, season):
        self.logger.debug("Fetching Season")
        return self.fetch('show.seasons&tvdbid=%s&season=%s' % (tvdbid, season))

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def SearchEpisodeDownload(self, tvdbid, season, episode):
        self.logger.debug("Fetching Episode Downloads")
        return self.fetch('episode.search&tvdbid=%s&season=%s&episode=%s' % (tvdbid, season, episode), False, 45)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def RemoveShow(self, tvdbid):
        self.logger.debug("Force full update for tvdbid %s" % tvdbid)
        return self.fetch("show.delete&tvdbid=%s" % tvdbid)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def ChangeStatus(self):
        self.logger.debug("Changing Show Status")
        form = cgi.FieldStorage()
        name = form.getfirst('statusSelect', 'empty')
        status = cgi.escape(statusSelect)
        episodes = form.getlist('changestatus')
        for each in episodes:
            tvdbid, season, episode = cgi.escape(each).split('|')
            self.fetch("episode.setstatus&tvdbid=%s&season=%s&episode=%s&status=%s" % (tvdbid, season, episode, status)) 
        return

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def Restart(self):
        self.logger.debug("Restarting Sickbeard")
        return self.fetch("sb.restart")

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def Shutdown(self):
        self.logger.debug("Shutting Down Sickbeard")
        return self.fetch("sb.shutdown")

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def ForceFullUpdate(self, tvdbid):
        self.logger.debug("Force full update for tvdbid %s" % tvdbid)
        return self.fetch("show.update&tvdbid=%s" % tvdbid)

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def RescanFiles(self, tvdbid):
        self.logger.debug("Rescan all local files for tvdbid %s" % tvdbid)
        return self.fetch("show.refresh&tvdbid=%s" % tvdbid)

    @cherrypy.expose()
    @require()
    def SearchShow(self, query):
        try:
            url = 'http://www.thetvdb.com/api/GetSeries.php?seriesname=%s' % quote(query)
            return urlopen(url, timeout=10).read()
        except:
            return

    def fetch(self, cmd, img=False, timeout=10):
        try:
            host = pytunes.settings.get('sickbeard_host', '')
            port = str(pytunes.settings.get('sickbeard_port', ''))
            apikey = pytunes.settings.get('sickbeard_apikey', '')
            ssl = 's' if pytunes.settings.get('sickbeard_ssl', 0) else ''
            sickbeard_basepath = pytunes.settings.get('sickbeard_basepath', '/')

            if not (sickbeard_basepath.endswith('/')):
                sickbeard_basepath += "/"
            url = 'http%s://%s:%s%sapi/%s/?cmd=%s' % (ssl, host, str(port), sickbeard_basepath, apikey, cmd)

            self.logger.debug("Fetching information from: %s" % url)

            if (img == True):
                return urlopen(url, timeout=timeout).read()

            return loads(urlopen(url, timeout=timeout).read())
        except:
            self.logger.error("Unable to fetch information")
            return
