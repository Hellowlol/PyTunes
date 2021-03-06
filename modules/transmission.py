#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
from pytunes.staticvars import get_var as html
from pytunes import settings
import urllib2
import base64
import datetime
from json import loads, dumps
import logging

class Transmission:
    # Transmission Session ID
    sessionId = ''

    def __init__(self):
        self.logger = logging.getLogger('modules.transmission')
        pytunes.MODULES.append({
            'name': 'Transmission',
            'id': 'transmission',
            'test': '%stransmission/ping' % pytunes.WEBDIR,
            'directions':'Most of these settings require a restart after saving. First hit the save button, and then the restart button.',            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'transmission_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'transmission_name', 'placeholder':''},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'transmission_host', 'placeholder':''},
                {'type': 'text', 'label': 'Port *', 'name': 'transmission_port', 'placeholder':'', 'desc':'Default is 9091'},
                {'type': 'text', 'label': 'Username', 'name': 'transmission_username'},
                {'type': 'password', 'label': 'Password', 'name': 'transmission_password'},
                {'type': 'text', 'label': 'Movie Directory', 'name': 'transmission_moviedir', 'dir':False},
                {'type': 'text', 'label': 'TV Directory', 'name': 'transmission_tvdir', 'dir':False},
                {'type': 'text', 'label': 'Music Directory', 'name': 'transmission_musicdir', 'dir':False},
                {'type': 'text', 'label': 'Music Video Directory', 'name': 'transmission_musicviddir', 'dir':False},
                {'type': 'text', 'label': 'Concert Directory', 'name': 'transmission_concertdir', 'dir':False},
                {'type': 'text', 'label': 'Anime Directory', 'name': 'transmission_animedir', 'dir':False},
                {'type': 'text', 'label': 'Other Directory', 'name': 'transmission_otherdir', 'dir':False}
        ]})

    @cherrypy.expose()
    def index(self):
        return pytunes.LOOKUP.get_template('transmission.html').render(scriptname='transmission')

    @cherrypy.expose()
    def sizeof(self, num):
        for x in ['B','KB','MB','GB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
        return "%3.1f %s" % (num, 'TB')

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def queue(self, filter):
        table = []
        bars = {
            'Queued': 'progress-default',
            'Paused': 'progress-default',
            'Stalled': 'progress-warning',
            'Error': 'progress-danger progress-striped active',
            'Finished': 'progress-success',
            'Seeding': 'progress-success',
            'Downloading': 'progress-success progress-striped active'
        }

        fields = ['id', 'name', 'error', 'errorString', 'isFinished', 'isStalled', 'peers', 'peersConnected', 'peersFrom',   'status', 'comment', 'downloadDir', 'percentDone', 'leftUntilDone', 'totalSize', 'isFinished', 'eta', 'rateDownload', 'rateUpload', 'uploadRatio', 'priorities', 'queuePosition', 'wanted', 'peersGettingFromUs', 'peersSendingToUs', 'peersConnected']
        queue = self.fetch('torrent-get', {'fields': fields})
        states = ['Paused', 'unknown', 'unknown', 'Queued', 'Downloading', 'unknown', 'Seeding'];
        count = len(queue['arguments']['torrents'])
        cats = self.get_cats()
        if count:
            for torrent in sorted(queue['arguments']['torrents'], key=lambda k: k['queuePosition']):
                cat_select = []
                selected = False
                barwidth = '%s%s' % (torrent['percentDone'] * 100, '%')
                ratio = 0.0 if torrent['uploadRatio'] == -1 else torrent['uploadRatio']
                eta = '&infin;' if torrent['eta'] < 0 else str(datetime.timedelta(seconds=torrent['eta']))
                for cat in cats:
                    if torrent['downloadDir'] == cats[cat] and not selected:
                        cat_select.append("<option value='%s' selected='true'>%s</option>" % (cats[cat], cat))
                        selected = True
                    else:
                        cat_select.append("<option value='%s'>%s</option>" % (cats[cat], cat))
                    categories = "<form><select title='Configure in Settings' torrid='%s' class='span2 select_cat'>%s</select></form>" % (torrent['id'], ''.join(cat_select))
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
                queuetop = html('trans_queuetop') % (torrent['id'], '0')
                queueup = html('trans_queueup') % (torrent['id'], str(torrent['queuePosition'] - 1))
                queuedown = html('trans_queuedown') % (torrent['id'], str(torrent['queuePosition'] + 1))
                queuebottom = html('trans_queuebottom') % (torrent['id'], str(count - 1))
                if torrent['queuePosition'] == 0:
                    queuepos = '%s%s' % (queuedown, queuebottom)
                elif torrent['queuePosition'] == count - 1:
                    queuepos = '%s%s' % (queuetop, queueup)
                else:
                    queuepos = '%s%s%s%s' % (queuetop, queueup, queuedown, queuebottom)
                if status == 'Paused':
                    status_out = status
                    buttons = '%s%s%s%s%s%s' % (html('trans_start') % torrent['id'], html('trans_start_now') % torrent['id'],  html('trans_remove') % torrent['id'], html('trans_remove_data') % torrent['id'], html('trans_files') % (torrent['id'], len(torrent['priorities'])), queuepos)
                if status == 'Downloading':
                    status_out = status
                    buttons = '%s%s%s%s%s%s' % (html('trans_pause') % torrent['id'], html('trans_remove') % torrent['id'], html('trans_remove_data') % torrent['id'], html('trans_reannounce') % torrent['id'], html('trans_files') % (torrent['id'], len(torrent['priorities'])), queuepos)
                if status == 'Queued':
                    status_out = status
                    buttons = '%s%s%s%s%s' % (html('trans_start_now') % torrent['id'], html('trans_pause') % torrent['id'], html('trans_remove_data') % torrent['id'], html('trans_files') % (torrent['id'], len(torrent['priorities'])), queuepos)
                if status == 'Seeding':
                    status_out = status
                    buttons = '%s%s%s%s' % (html('trans_pause') % torrent['id'], html('trans_remove') % torrent['id'], html('trans_remove_data') % torrent['id'], html('trans_files') % (torrent['id'], len(torrent['priorities'])))
                if status == 'Finished':
                    status_out = status
                    buttons = '%s%s%s' % (html('trans_remove') % torrent['id'], html('trans_remove_data') % torrent['id'], html('trans_files') % (torrent['id'], len(torrent['priorities'])))
                if status == 'Stalled':
                    status_out = status
                    buttons = '%s%s%s%s%s%s' % (html('trans_pause') % torrent['id'], html('trans_remove') % torrent['id'], html('trans_remove_data') % torrent['id'], html('trans_reannounce') % torrent['id'], html('trans_files') % (torrent['id'], len(torrent['priorities'])), queuepos)
                if status == 'Error':
                    buttons = '%s%s' % (html('trans_remove') % torrent['id'], html('trans_remove_data') % str(torrent['id']))
                    status_out = html('trans_error') % torrent['errorString']
                if filter == 'All' or filter == status:
                    table.append(html('trans_row') % (torrent['id'], torrent['name'], dlrate, ulrate, torrent['peersConnected'], torrent['peersSendingToUs'], torrent['peersGettingFromUs'], categories, ratio, total, eta, left, status_out, bars[status], barwidth, barwidth, buttons))
            return ''.join(table).replace("\n", "")
        else:
            return '<tr><td>Queue is Empty</td></tr>'

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def stats(self):
        stats = self.fetch('session-stats')
        session = self.fetch('session-get')
        speed = {'up': session['arguments']['speed-limit-up'], 'down': session['arguments']['speed-limit-down']}
        return stats

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def session(self):
        session = self.fetch('session-get')
        cats = {'up': session['arguments']['speed-limit-up'], 'down': session['arguments']['speed-limit-down']}
        return session

    def get_cats(self):
        session = self.fetch('session-get')
        cats = {'Default': session['arguments']['download-dir']}
        dirs = {
            'transmission_moviedir': 'Movies',
            'transmission_tvdir': 'TV',
            'transmission_musicdir': 'Music',
            'transmission_musicviddir': 'Music Videos',
            'transmission_dirconcert': 'Concerts',
            'transmission_aminedir': 'Anime',
            'transmission_dirother': 'Other'
        }
        for dir in dirs:
            val = settings.get(dir)
            if val:
                cats[dirs[dir]] = val
        return cats

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def start(self, torrentId = False):
        if (torrentId == False) :
            return self.fetch('torrent-start')
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-start', {'ids': torrentId})

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def pause(self, torrentId = False):
        if (torrentId == False) :
            return self.fetch('torrent-pause')
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-start-now', {'ids': torrentId})

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def start_now(self, torrentId = False):
        if (torrentId == False) :
            return self.fetch('torrent-start-now')
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-start-now', {'ids': torrentId})

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def stop(self, torrentId = False):
        if (torrentId == False) :
            return self.fetch('torrent-stop')
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-stop', {'ids': torrentId})

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def reannounce(self, torrentId):
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-reannounce', {'ids': torrentId})

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
    def to_client2(self, data):
        #print 'info: ', data
        try:
            self.logger.info('Added torrent info to Transmission from file')
            return self.fetch('torrent-add', {'metainfo': info})
        except Exception as e:
            self.logger.error('Failed to add torrent %s file to Transmission %s' % (info, e))

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def remove(self, torrentId, deletedata = False):
        try:
            torrentId = int(torrentId)
        except ValueError:
            return False
        return self.fetch('torrent-remove', {'ids': torrentId, 'delete-local-data': deletedata})

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def Queue_Move(self, id, pos):
        return self.fetch('torrent-set', {'ids': int(id), 'queuePosition': int(pos)})

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def ChangeCat(self, id, dir):
        #print id, dir
        return self.fetch('torrent-set-location', {'ids': int(id), 'location': dir, 'move': False})

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def files(self, id):
        files = self.fetch('torrent-get', {'ids': int(id), 'fields': ['files']})
        files = files['arguments']['torrents'][0]['files']
        filestats = self.fetch('torrent-get', {'ids': int(id), 'fields': ['fileStats']})
        filestats = filestats['arguments']['torrents'][0]['fileStats']
        return filestats
        i = 0
        #for file in files['arguments']['torrents'][0]['files']:
        #    print file


    # Wrapper to access the Transmission Api
    # If the first call fails, there probably is no valid Session ID so we try it again
    def fetch(self, method, arguments=''):
        """ Do request to Transmission api """
        self.logger.debug("Request transmission method: %s" % method)

        host = settings.get('transmission_host', '')
        port = str(settings.get('transmission_port', ''))

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

