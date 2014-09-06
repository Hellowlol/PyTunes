#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
from pytunes.staticvars import get_var as html
import urllib2
import base64
from json import loads, dumps
import logging
from cherrypy.lib.auth2 import require

class Transmission:
    # Transmission Session ID
    sessionId = ''

    def __init__(self):
        self.logger = logging.getLogger('modules.transmission')
        pytunes.MODULES.append({
            'name': 'Transmission',
            'id': 'transmission',
            'test': '%stransmission/ping' % pytunes.WEBDIR,
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'transmission_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'transmission_name', 'placeholder':''},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'transmission_host', 'placeholder':''},
                {'type': 'text', 'label': 'Port *', 'name': 'transmission_port', 'placeholder':'', 'desc':'Default is 9091'},
                {'type': 'text', 'label': 'Username', 'name': 'transmission_username'},
                {'type': 'password', 'label': 'Password', 'name': 'transmission_password'},
                {'type': 'text', 'label': 'Movie Directory', 'name': 'transmission_moviedir', 'dir':False},
                {'type': 'text', 'label': 'TV Directory', 'name': 'transmission_tvdir', 'dir':False},
                {'type': 'text', 'label': 'Music Directory', 'name': 'transmission_musicdir', 'dir':False},
                {'type': 'text', 'label': 'Music Vid Directory', 'name': 'transmission_musicviddir', 'dir':False},
                {'type': 'text', 'label': 'Concert Directory', 'name': 'transmission_concertdir', 'dir':False},
                {'type': 'text', 'label': 'Anime Directory', 'name': 'transmission_animedir', 'dir':False},
                {'type': 'text', 'label': 'Other Directory', 'name': 'transmission_otherdir', 'dir':False}
        ]})

    @cherrypy.expose()
    @require()
    def index(self):
        return pytunes.LOOKUP.get_template('transmission.html').render(scriptname='transmission')

    @cherrypy.expose()
    @require()
    def sizeof(self, num):
        for x in ['B','KB','MB','GB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
        return "%3.1f %s" % (num, 'TB')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def queue(self):
        table = []
        fields = ['id', 'name', 'error', 'errorstring', 'isFinished', 'isStalled', 'peers', 'peersConnected', 'peersFrom',   'status', 'comment', 'downloadDir', 'percentDone', 'leftUntilDone', 'totalSize', 'isFinished', 'eta', 'rateDownload', 'rateUpload', 'uploadRatio', 'priorities', 'queuePosition', 'wanted']
        queue = self.fetch('torrent-get', {'fields': fields})
        states = ['Paused', 'unknown', 'unknown', 'Queued', 'Downloading', 'unknown', 'Seeding'];
        print queue
        count = len(queue['arguments']['torrents'])
        print 'count: ', count
        if count:
            for torrent in queue['arguments']['torrents']:
                barwidth = '%s%s' % (torrent['percentDone'] * 100, '%')
                ratio = 0.0 if torrent['uploadRatio'] == -1 else torrent['uploadRatio']
                eta = '&infin;' if torrent['eta'] == -1 else str(torrent['eta'])
                status = 'Unknown'
                if states[torrent['status']] != 'unknown':
                    status = states[torrent['status']]
                if torrent['isFinished']:
                    status = 'Finished'
                if torrent['isStalled']:
                    status = 'Stalled'
                elif torrent['error']:
                    status = 'Error'
                dlrate = self.sizeof(torrent['rateDownload'])
                ulrate = self.sizeof(torrent['rateUpload'])
                total = self.sizeof(torrent['totalSize'])
                left = self.sizeof(torrent['leftUntilDone'])
                queuetop = "<a href='#' class='queue btn btn-mini' action='top' id='%s' newpos='0' title='Top'><i class='icon-long-arrow-up'></i></a>" % torrent['id']
                queueup = "<a href='#' class='queue btn btn-mini' action='up' id='%s' newpos='%s' title='Up 1 Level'><i class='icon-level-up'></i></a>" % (torrent['id'], str(torrent['queuePosition'] + 1))
                queuedown = "<a href='#' class='queue btn btn-mini' action='down' id='%s' newpos='%s' title='Down 1 Level'><i class='icon-level-down'></i></a>" % (torrent['id'], str(torrent['queuePosition'] - 1))
                queuebottom = "<a href='#' class='queue btn btn-mini' action='bottom' id='%s' newpos='%s' title='Bottom'><i class='icon-long-arrow-down'></i></a>" % (torrent['id'], str(count - 1))
                if torrent['queuePosition'] == 0:
                    queuepos = '%s%s' % (queuedown, queuebottom)
                elif torrent['queuePosition'] == count - 1:
                    queuepos = '%s%s' % (queuetop, queueup)
                else:
                    queuepos = '%s%s%s%s' % (queuetop, queueup, queuedown, queuebottom)
                table.append(html('trans_row') % (torrent['id'], torrent['name'], dlrate, ulrate, torrent['downloadDir'], ratio, torrent['priorities'], queuepos, left, total, eta, status, torrent['isFinished'], torrent['isStalled'], torrent['error'], 'progress-default', barwidth))
            return ''.join(table).replace("\n", "")
        else:
            return '<tr><td>Queue is Empty</td></tr>'

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def stats(self):
        return self.fetch('session-stats')

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def start(self, torrentId = False):
        if (torrentId == False) :
            return self.fetch('torrent-start-now')
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-start-now', {'ids': torrentId})

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def stop(self, torrentId = False):
        if (torrentId == False) :
            return self.fetch('torrent-stop')
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-stop', {'ids': torrentId})

    #For torrent search
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def to_client(self, link):
        try:
            self.logger.info('Added torrent link to Transmission')
            return self.fetch('torrent-add', {'filename': link})
        except Exception as e:
            self.logger.debug('Failed to add torrent %s link to Transmission %s' % (link, e))

    #For torrent upload have to be base 64 encode
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def to_client2(self, info):
        try:
            self.logger.info('Added torrent info to Transmission from file')
            return self.fetch('torrent-add', {'metainfo': info})
        except Exception as e:
            self.logger.debug('Failed to add torrent %s file to Transmission %s' % (info, e))

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def remove(self, torrentId, deletedata = False):
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-remove', {'ids': torrentId, 'delete-local-data': deletedata})

    # Wrapper to access the Transmission Api
    # If the first call fails, there probably is no valid Session ID so we try it again
    def fetch(self, method, arguments=''):
        """ Do request to Transmission api """
        self.logger.debug("Request transmission method: %s" % method)

        host = pytunes.settings.get('transmission_host', '')
        port = str(pytunes.settings.get('transmission_port', ''))

        url = 'http://%s:%s/transmission/rpc/' % (host, str(port))

        # format post data
        data = {'method': method}
        if (arguments != ''):
            data['arguments'] =  arguments
        data = dumps(data)

        # Set Header
        header = {
            'X-Transmission-Session-Id': self.sessionId,
            'Content-Type': 'json; charset=UTF-8'
        }

        # Add authentication
        authentication = self.auth()
        if (authentication) :
            header['Authorization'] = "Basic %s" % authentication

        try:
            request = urllib2.Request(url, data=data, headers=header)
            response = urllib2.urlopen(request).read()
            return loads(response)
        except urllib2.HTTPError, e:
             # Fetching url failed Maybe Transmission session must be renewed
            if (e.getcode() == 409 and e.headers['X-Transmission-Session-Id']) :
                self.logger.debug("Setting new session ID provided by Transmission")

                # If response is 409 re-set session id from header
                self.sessionId = e.headers['X-Transmission-Session-Id']

                self.logger.debug("Retry Transmission api with new session id.")
                try:
                    header['X-Transmission-Session-Id'] = self.sessionId

                    req = urllib2.Request(url, data=data, headers=header)
                    response = urllib2.urlopen(req).read()
                    return loads(response)
                except:
                    self.logger.error("Unable access Transmission api with new session id.")
                    return
        except Exception:
            self.logger.error("Unable to fetch information from: %s" % url)
            return


    # Construct url with login details
    def auth(self):
        """ Generate a base64 HTTP auth string based on settings """
        self.logger.debug("Generating authentication string for transmission")

        password = pytunes.settings.get('transmission_password', '')
        username = pytunes.settings.get('transmission_username', '')

        if username != '' and password != '':
            return base64.encodestring('%s:%s' % (username, password)).replace('\n', '')

        return False
