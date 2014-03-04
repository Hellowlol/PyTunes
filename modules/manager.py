""" Module for Media Management  """
import cherrypy
import htpc
import base64
import socket
import struct
import json
import simplejson
from htpc.xdb import table_dump
from itertools import chain
from urllib2 import quote, unquote
from jsonrpclib import Server
from sqlobject import SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol, IntCol
from htpc.proxy import get_image
import logging

""" SQLObject class for album table """
class Album(SQLObject):
    idAlbum = IntCol()
    strAlbum = StringCol()
    strArtists = StringCol()
    strGenres = StringCol()
    iYear = IntCol()
    idAlbumInfo = IntCol()
    strMoods = StringCol()
    strStyles = StringCol()
    strThemes = StringCol()
    strReview = StringCol()
    strLabel = StringCol()
    strType = StringCol()
    strImage = StringCol()
    iRating = IntCol()
    iTimesPlayed = IntCol()
    bCompilation = IntCol()
    MusicBrainzArtistID = StringCol()
    MusicBrainzAlbumID = StringCol()
    MusicBrainzGroupID = StringCol()

""" SQLObject class for discography table """
class Discography(SQLObject):
    idArtist = IntCol()
    strArtist = StringCol()
    strYear = StringCol()
    strAlbum = StringCol()
    MusicBrainzArtistID = StringCol()
    MusicBrainzAlbumID = StringCol()
    MusicBrainzGroupID = StringCol()
    
""" SQLObject class for artist table """
class Artist(SQLObject):
    idArtist = IntCol()
    strArtist = StringCol()
    strBorn = StringCol()
    strFormed = StringCol()
    strGenres = StringCol()
    strMoods = StringCol()
    strStyles = StringCol()
    strInstruments = StringCol()
    strBiography = StringCol()
    strDied = StringCol()
    strDisbanded = StringCol()
    strYearsActive = StringCol()
    strImage = StringCol()
    strFanart = StringCol()
    MusicBrainzArtistID = StringCol()

""" SQLObject class for song table """
class Song(SQLObject):
    idSong = IntCol()
    strArtists = StringCol()
    strGenres = StringCol()
    strTitle = StringCol()
    iTrack = IntCol()
    iStartOffset = IntCol()
    iEndOffset = IntCol()
    iTimesPlayed = IntCol()
    iDuration = IntCol()
    iYear = IntCol()
    dwFileNameCRC = StringCol()
    strFileName = StringCol()
    MusicBrainzTrackID = StringCol()
    MusicBrainzArtistID = StringCol()
    MusicBrainzAlbumID = StringCol()
    MusicBrainzAlbumArtisID = StringCol()
    MusicBrainzTRMID = StringCol()
    rating = IntCol()
    lastplayed = IntCol()
    idAlbum = IntCol()
    iKaraNumber = IntCol()
    iKaraDelay = IntCol()
    strKaraEncoding = StringCol()
    bCompilation = IntCol()
    strAlbumArtists = StringCol()
    strAlbum = StringCol()
    strPath = StringCol()
    comment = StringCol()

""" SQLObject class for music_art table """
class MusicArt(SQLObject): 
    media_id = IntCol()
    media_type = StringCol()
    type = StringCol()
    url = StringCol()   

    
class Manager:
    def __init__(self):
        """ Add module to list of modules on load and set required settings """
        self.logger = logging.getLogger('modules.manager')

        Album.createTable(ifNotExists=True)
        Discography.createTable(ifNotExists=True)
        Artist.createTable(ifNotExists=True)
        Song.createTable(ifNotExists=True)
        MusicArt.createTable(ifNotExists=True)
        htpc.MODULES.append({
            'name': 'Media Manager',
            'id': 'manager',
            'fields': [
                {'type':'bool', 'label':'Enable', 'name':'manager_enable'},
                {'type':'text', 'label':'Menu name', 'name':'manager_name'},
                {'type':'text', 'label':'Fanart.tv Apikey', 'name':'fatv_apikey'},
                {'type':'bool', 'label':'Fanart.tv Use SSL', 'name':'fatv_ssl'},
                {'type':'text', 'label':'Last.fm Apikey', 'name':'lastfm_apikey'},
                {'type':'bool', 'label':'Last.fm Use SSL', 'name':'lastfm_ssl'},
                {'type':'text', 'label':'TMDB Apikey', 'name':'tmdb_apikey'},
                {'type':'bool', 'label':'TMDB Use SSL', 'name':'tmdb_ssl'}
        ]})

    @cherrypy.expose()
    def index(self):
        """ Generate page from template """
        #data = table_dump('music.db', 'artistview')
        return htpc.LOOKUP.get_template('manager.html').render(scriptname='manager')


    @cherrypy.expose()
    def ViewAlbum(self, album_id):
        response = self.fetch('getAlbum&id=%s' % album_id)

        tracks = response['tracks']
        for t in tracks:
            duration = t['TrackDuration']
            total_seconds = duration / 1000
            minutes = total_seconds / 60
            seconds = total_seconds - (minutes * 60)
            t['DurationText'] = '%d:%02d' % (minutes, seconds)
            t['TrackStatus'] = _get_status_icon('Downloaded' if t['Location'] is not None else '')

        template = htpc.LOOKUP.get_template('xbmc_album.html')
        return template.render(
            scriptname=None,
            artist_id=response['album'][0]['ArtistID'],
            album_id=album_id,
            module_name=htpc.settings.get('xbmc_name') or 'XBMC',
            album=response['album'][0],
            tracks=response['tracks'],
            description=response['description'][0],
        )

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetArtist(self, artist_id):
        """ Get data of a specific artist """
        self.logger.debug("Get data of a specific artist")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            properties = ['musicbrainzartistid', 'thumbnail', 'fanart', 'style', 'died', 'born', 'formed', 'mood', 'disbanded', 'instrument', 'yearsactive', 'description']
            return xbmc.AudioLibrary.GetArtistDetails(artistid=int(artist_id), properties=properties)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch artist info!")
            return


    @cherrypy.expose()
    def ViewArtist(self, artist_id, artist):
        """ Load artist template """
        self.logger.debug("Get data of a specific artist")
        template = htpc.LOOKUP.get_template('xbmc_artist.html')
        return template.render(
            scriptname='xbmc_artist',
            artist_id=artist_id,
            name=artist
        )

    @cherrypy.expose()
    def GetThumb(self, thumb=None, h=None, w=None, o=100):
        """ Parse thumb to get the url and send to htpc.proxy.get_image """
        url = self.url('/images/DefaultVideo.png')
        if thumb:
            url = self.url('/image/' + quote(thumb))

        self.logger.debug("Trying to fetch image via " + url)
        return get_image(url, h, w, o, self.auth())

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetMovies(self, start=0, end=0, sortmethod='title', sortorder='ascending', hidewatched=0, filter=''):
        """ Get a list of all movies """
        self.logger.debug("Fetching Movies")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            sort = {'order': sortorder, 'method': sortmethod, 'ignorearticle': True}
            properties = ['title', 'year', 'plot', 'thumbnail', 'file', 'fanart', 'studio', 'trailer',
                    'imdbnumber', 'genre', 'rating', 'playcount', 'cast', 'writer', 'director', 'country', 'runtime', 'mpaa', 'streamdetails']
            limits = {'start': int(start), 'end': int(end)}
            filter = {'field': 'title', 'operator': 'contains', 'value': filter}
            if hidewatched == "1":
                filter = {"and": [filter, {'field': 'playcount', 'operator': 'is', 'value': '0'}]}
            return xbmc.VideoLibrary.GetMovies(sort=sort, properties=properties, limits=limits, filter=filter)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch movies!")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetShows(self, start=0, end=0, sortmethod='title', sortorder='ascending', hidewatched=0, filter=''):
        """ Get a list of all the TV Shows """
        self.logger.debug("Fetching TV Shows")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            sort = {'order': sortorder, 'method': sortmethod, 'ignorearticle': True}
            properties = ['title', 'year', 'plot', 'thumbnail', 'playcount']
            limits = {'start': int(start), 'end': int(end)}
            filter = {'field': 'title', 'operator': 'contains', 'value': filter}
            if hidewatched == "1":
                filter = {"and": [filter, {'field': 'playcount', 'operator': 'is', 'value': '0'}]}
            shows = xbmc.VideoLibrary.GetTVShows(sort=sort, properties=properties, limits=limits, filter=filter)
            return shows
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch TV Shows")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetEpisodes(self, start=0, end=0, sortmethod='episode', sortorder='ascending', tvshowid=None, hidewatched=False, filter=''):
        """ Get information about a single TV Show """
        self.logger.debug("Loading information for TVID" + str(tvshowid))
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            sort = {'order': sortorder, 'method': sortmethod, 'ignorearticle': True}
            properties = ['episode', 'season', 'thumbnail', 'plot', 'file', 'playcount']
            limits = {'start': int(start), 'end': int(end)}
            filter = {'field': 'title', 'operator': 'contains', 'value': filter}
            if hidewatched == "1":
                filter = {"and": [filter, {'field': 'playcount', 'operator': 'is', 'value': '0'}]}
            episodes = xbmc.VideoLibrary.GetEpisodes(sort=sort, tvshowid=int(tvshowid), properties=properties, limits=limits, filter=filter)
            return episodes
        except:
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetArtists(self, start=0, end=0, sortmethod='artist', sortorder='ascending', filter=''):
        """ Get a list of all artists """
        self.logger.debug("Fetching all artists in the music database")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            sort = {'order': sortorder, 'method': sortmethod, 'ignorearticle': True}
            properties = ['musicbrainzartistid', 'thumbnail', 'fanart']
            limits = {'start': int(start), 'end': int(end)}
            filter = {'field': 'artist', 'operator': 'contains', 'value': filter}
            return xbmc.AudioLibrary.GetArtists(properties=properties, limits=limits, sort=sort, filter=filter, albumartistsonly=True)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch artists!")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetAlbums(self, start=0, end=0, sortmethod='label', sortorder='ascending', artistid=None, filter=''):
        """ Get a list of all albums for artist """
        self.logger.debug("Loading all albums for ARTISTID " + str(artistid))
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            sort = {'order': sortorder, 'method': sortmethod, 'ignorearticle': True}
            properties = ['title', 'artist', 'year', 'thumbnail']
            limits = {'start': int(start), 'end': int(end)}
            if artistid:
                filter = {'artistid': int(artistid)}
            else:
                filter = {'or': [{'field': 'album', 'operator': 'contains', 'value': filter},
                                 {'field': 'artist', 'operator': 'contains', 'value': filter}]}
            return xbmc.AudioLibrary.GetAlbums(properties=properties, limits=limits, sort=sort, filter=filter)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch albums!")
            return
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetSongs(self, start=0, end=0, albumid=None, artistid=None, filter='', *args, **kwargs):
        """ Get a list of all songs """
        self.logger.debug("Fetching all artists in the music database")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            sort = {'order': sortorder, 'method': sortmethod, 'ignorearticle': True}
            properties = ['artist', 'artistid', 'album', 'albumid', 'duration', 'year', 'thumbnail']
            limits = {'start': int(start), 'end': int(end)}
            if albumid and filter == '':
                filter = {'albumid': int(albumid)}
            elif artistid and filter == '':
                filter = {'artistid': int(artistid)}
            else:
                filter = {'or': [{'field': 'album', 'operator': 'contains', 'value': filter},
                                 {'field': 'artist', 'operator': 'contains', 'value': filter},
                                 {'field': 'title', 'operator': 'contains', 'value': filter}]}

            return xbmc.AudioLibrary.GetSongs(properties=properties, limits=limits, sort=sort, filter=filter)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch artists!")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetChannelGroups(self, type='tv'):
        """ Get PVR channel list from xbmc """
        self.logger.debug("Loading XBMC PVC channel list.")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            return xbmc.PVR.GetChannelGroups(channeltype=type)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch channelgroups!")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetChannels(self, type='tv', group=2):
        """ Get PVR channel list from xbmc """
        self.logger.debug("Loading XBMC PVC channel list.")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            return xbmc.PVR.GetChannels(channelgroupid=int(group), properties=['thumbnail'])
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch channels!")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def PlayItem(self, item=None, type=None):
        """ Play a file in XBMC """
        self.logger.debug("Playing '" + item + "' of the type " + type)
        xbmc = Server(self.url('/jsonrpc', True))
        if type == 'movie':
            return xbmc.Player.Open(item={'movieid': int(item)}, options={'resume': True})
        elif type == 'episode':
            return xbmc.Player.Open(item={'episodeid': int(item)}, options={'resume': True})
        elif type == 'channel':
            return xbmc.Player.Open(item={'channelid': int(item)})
        elif type == 'artist':
            return xbmc.Player.Open(item={'artistid': int(item)})
        elif type == 'album':
            return xbmc.Player.Open(item={'albumid': int(item)})
        elif type == 'song':
            return xbmc.Player.Open(item={'songid': int(item)})
        else:
            return xbmc.Player.Open(item={'file': item})

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def QueueItem(self, item, type):
        """ Queue a file in XBMC """
        self.logger.debug("Enqueueing '" + item + "' of the type " + type)
        xbmc = Server(self.url('/jsonrpc', True))
        if type == 'movie':
            return xbmc.Playlist.Add(playlistid=1, item={'movieid': int(item)})
        elif type == 'episode':
            return xbmc.Playlist.Add(playlistid=1, item={'episodeid': int(item)})
        elif type == 'channel':
            return xbmc.Playlist.Add(playlistid=1, item={'channelid': int(item)})
        elif type == 'artist':
            return xbmc.Playlist.Add(playlistid=0, item={'artistid': int(item)})
        elif type == 'album':
            return xbmc.Playlist.Add(playlistid=0, item={'albumid': int(item)})
        elif type == 'song':
            return xbmc.Playlist.Add(playlistid=0, item={'songid': int(item)})

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def RemoveItem(self, item, playlistid=0):
        """ Remove a file from the playlist """
        self.logger.debug("Removing '" + item + "' from the playlist")
        xbmc = Server(self.url('/jsonrpc', True))
        return xbmc.Playlist.Remove(playlistid=playlistid, position=int(item))

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def LibraryRemoveItem(self, libraryid, media):
        """ Remove an entry from the database """
        self.logger.debug("Removing '" + libraryid + "' from the database")
        xbmc = Server(self.url('/jsonrpc', True))
        if media == 'movie':
            return xbmc.VideoLibrary.RemoveMovie(movieid=int(libraryid))
        elif media == 'musicvideo':
            return xbmc.VideoLibrary.RemoveMusicVideo(musicvideoid=int(libraryid))
        elif media == 'tvshow':
            return xbmc.VideoLibrary.RemoveTVShow(tvshowid=int(libraryid))
        elif media == 'episode':
            return xbmc.VideoLibrary.RemoveEpisode(episodeid=int(libraryid))

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def ExecuteAddon(self, addon, cmd0, cmd1):
        """ Execute an XBMC addon """
        self.logger.debug("Execute '" + addon + "' with commands '" + cmd0 + "' and '" + cmd1 +"'")
        xbmc = Server(self.url('/jsonrpc', True))
        if addon == 'script.artwork.downloader':
            return xbmc.Addons.ExecuteAddon(addon)
        elif addon == 'script.cinema.experience':
            cmd = 'movieid=' + int(cmd0)
            return xbmc.Addons.ExecuteAddon(addon, cmd)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def PlaylistMove(self, position1, position2, playlistid=0):
        """ Swap files in playlist """
        playlistid = int(playlistid)
        position1 = int(position1)
        position2 = int(position2)
        i = 1 if position1 < position2 else -1
        xbmc = Server(self.url('/jsonrpc', True))
        while(position1 != position2):
            xbmc.Playlist.Swap(playlistid=playlistid, position1=position1, position2=position1 + i)
            position1 += i
        return "Moved from " + str(position1) + " to " + str(position2)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def Playlist(self, type='audio'):
        """ Get a playlist from XBMC """
        self.logger.debug("Loading Playlist of type " + type)
        xbmc = Server(self.url('/jsonrpc', True))
        if type == 'video':
            return xbmc.Playlist.GetItems(playlistid=1, properties=['year', 'showtitle', 'season', 'episode', 'runtime'])

        return xbmc.Playlist.GetItems(playlistid=0, properties=['artist', 'title', 'album', 'duration'])

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def NowPlaying(self):
        """ Get information about current playing item """
        self.logger.debug("Fetching currently playing information")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            player = xbmc.Player.GetActivePlayers()[0]
            playerid = player['playerid']

            if player['type'] == 'video':
                playerprop = ['speed', 'position', 'time', 'totaltime',
                              'percentage', 'subtitleenabled', 'currentsubtitle',
                              'subtitles', 'currentaudiostream', 'audiostreams']
                itemprop = ['thumbnail', 'showtitle', 'season', 'episode', 'year', 'fanart']

            elif player['type'] == 'audio':
                playerprop = ['speed', 'position', 'time', 'totaltime', 'percentage']
                itemprop = ['thumbnail', 'title', 'artist', 'album', 'year', 'fanart']

            app = xbmc.Application.GetProperties(properties=['muted', 'volume'])
            player = xbmc.Player.GetProperties(playerid=playerid, properties=playerprop)
            item = xbmc.Player.GetItem(playerid=playerid, properties=itemprop)

            return {'playerInfo': player, 'itemInfo': item, 'app': app}
        except IndexError:
            self.logger.debug("Nothing current playing.")
            return
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch currently playing information!")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def ControlPlayer(self, action, value=''):
        """ Various commands to control XBMC Player """
        self.logger.debug("Sending control to XBMC: " + action)
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            if action == 'seek':
                player = xbmc.Player.GetActivePlayers()[0]
                return xbmc.Player.Seek(playerid=player[u'playerid'], value=float(value))
            elif action == 'jump':
                player = xbmc.Player.GetActivePlayers()[0]
                return xbmc.Player.GoTo(playerid=player[u'playerid'], to=int(value))
            elif action == 'party':
                return xbmc.Player.Open(item={'partymode': 'audio'})
            elif action == 'fullscreen':
                return xbmc.GUI.SetFullscreen(fullscreen='toggle')
            else:
                return xbmc.Input.ExecuteAction(action=action)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to control XBMC with action: " + action)
            return 'error'


    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def SendText(self, text):
        """ Send text to XBMC """
        self.logger.debug("Sending text to XBMC: " + text)
        xbmc = Server(self.url('/jsonrpc', True))
        return xbmc.Input.SendText(text=text)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def Subtitles(self, subtitle='off'):
        """ Change the subtitles """
        self.logger.debug("Changing subtitles to " + subtitle)
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            playerid = xbmc.Player.GetActivePlayers()[0][u'playerid']
            try:
                subtitle = int(subtitle)
                xbmc.Player.SetSubtitle(playerid=playerid, subtitle=subtitle, enable=True)
                return "success"
            except ValueError:
                xbmc.Player.SetSubtitle(playerid=playerid, subtitle='off')
                return "Disabling subtitles."
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to set subtitle to specified value " + subtitle)
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def Audio(self, audio):
        """ Change the audio stream  """
        self.logger.debug("Changing audio stream to " + audio)
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            playerid = xbmc.Player.GetActivePlayers()[0][u'playerid']
            return xbmc.Player.SetAudioStream(playerid=playerid, stream=int(audio))
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to change audio stream to specified value " + audio)
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def System(self, action=''):
        """ Various system commands """
        xbmc = Server(self.url('/jsonrpc', True))
        if action == 'shutdown-server':
            self.logger.info("Shutting down Server")
            xbmc.System.Shutdown()
            return 'Shutting down Server.'
        elif action == 'suspend-server':
            self.logger.info("Suspending Server")
            xbmc.System.Suspend()
            return 'Suspending Server.'
        elif action == 'reboot-server':
            self.logger.info("Rebooting Server")
            xbmc.System.Reboot()
            return 'Rebooting Server.'
        elif action == 'wake-xbmc':
            self.logger.info("Waking Up XBMC")
            xbmc.System.OnWake()
            return 'Waking UP XBMC.'
        elif action == 'shutdown-xbmc':
            self.logger.info("Shutting down XBMC")
            xbmc.System.OnQuit()
            return 'Shutting down XBMC.'
        elif action == 'suspend-xbmc':
            self.logger.info("Suspending XBMC")
            xbmc.System.OnSleep()
            return 'Suspending XBMC.'
        elif action == 'reboot-xbmc':
            self.logger.info("Rebooting XBMC")
            xbmc.System.OnRestart()
            return 'Rebooting XBMC.'

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def Wake(self):
        """ Send WakeOnLan package """
        self.logger.info("Waking up XBMC-System")
        try:
            addr_byte = self.current.mac.split(':')
            hw_addr = struct.pack('BBBBBB',
            int(addr_byte[0], 16),
            int(addr_byte[1], 16),
            int(addr_byte[2], 16),
            int(addr_byte[3], 16),
            int(addr_byte[4], 16),
            int(addr_byte[5], 16))
            msg = '\xff' * 6 + hw_addr * 16
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(msg, ("255.255.255.255", 9))
            self.logger.info("WOL package sent to " + self.current.mac)
            return "WOL package sent"
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to send WOL packet")
            return "Unable to send WOL packet"

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def Notify(self, text):
        """ Create popup in XBMC """
        self.logger.debug("Sending notification to XBMC: " + text)
        xbmc = Server(self.url('/jsonrpc', True))
        image = 'https://raw.github.com/styxit/HTPC-Manager/master/interfaces/default/img/xbmc-logo.png'
        return xbmc.GUI.ShowNotification(title='PyTunes', message=text, image=image)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetRecentMovies(self, limit=5):
        """ Get a list of recently added movies """
        self.logger.debug("Fetching recently added movies")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            properties = ['title', 'year', 'runtime', 'plot', 'thumbnail', 'file',
                          'fanart', 'trailer', 'imdbnumber', 'studio', 'genre', 'rating']
            limits = {'start': 0, 'end': int(limit)}
            return xbmc.VideoLibrary.GetRecentlyAddedMovies(properties=properties, limits=limits)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch recently added movies!")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetRecentShows(self, limit=5):
        """ Get a list of recently added TV Shows """
        self.logger.debug("Fetching recently added TV Shows")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            properties = ['showtitle', 'season', 'episode', 'title', 'runtime',
                          'thumbnail', 'plot', 'fanart', 'file']
            limits = {'start': 0, 'end': int(limit)}
            return xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties=properties, limits=limits)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch recently added TV Shows")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetRecentAlbums(self, limit=5):
        """ Get a list of recently added music """
        self.logger.debug("Fetching recently added Music")
        try:
            xbmc = Server(self.url('/jsonrpc', True))
            properties = ['artist', 'albumlabel', 'year', 'description', 'thumbnail']
            limits = {'start': 0, 'end': int(limit)}
            return xbmc.AudioLibrary.GetRecentlyAddedAlbums(properties=properties, limits=limits)
        except Exception, e:
            self.logger.debug("Exception: " + str(e))
            self.logger.error("Unable to fetch recently added Music!")
            return

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def Library(self, do='scan', lib='video'):
        xbmc = Server(self.url('/jsonrpc', True))
        if lib == 'video':
            if do == 'clean':
                return xbmc.VideoLibrary.Clean()
            elif do == 'export':
                return xbmc.VideoLibrary.Export()
            else:
                return xbmc.VideoLibrary.Scan()
        else:
            if do == 'clean':
                return xbmc.AudioLibrary.Clean()
            elif do == 'export':
                return xbmc.AudioLibrary.Export()
            else:
                return xbmc.AudioLibrary.Scan()

    def url(self, path='', auth=False):
        """ Generate a URL for the RPC based on XBMC settings """
        self.logger.debug("Generate URL to call XBMC")
        url = self.current.host + ':' + str(self.current.port) + path
        if auth and self.current.username and self.current.password:
            url = self.current.username + ':' + self.current.password + '@' + url

        self.logger.debug("URL: http://" + url)
        return 'http://' + url

    def auth(self):
        """ Generate a base64 HTTP auth string based on settings """
        self.logger.debug("Generating authentication string")
        if self.current.username and self.current.password:
            return base64.encodestring('%s:%s' % (self.current.username, self.current.password)).strip('\n')
