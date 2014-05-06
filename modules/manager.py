""" Module for Media Management  """
import cherrypy
import pytunes
from pytunes import tmdb, staticvars, scheduler
from pytunes.staticvars import get_var as html
from pytunes.proxy import get_image
import time
import threading
import base64
import socket
import struct
import json
import simplejson as json
from cherrypy.process.plugins import Monitor
from pytunes.xdb import *
from itertools import chain
from urllib2 import quote, unquote
from jsonrpclib import Server
from sqlobject import SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol, IntCol, FloatCol
import logging

musicvideo_schema_map = {
'c00': 'strTitle',
'c01': 'strThumb',
'c02': 'strUnknown',
'c03': 'strPlayCount',
'c04': 'strRuntime',
'c05': 'strDirector',
'c06': 'strStudios',
'c07': 'strYear',
'c08': 'strPlot',
'c09': 'strAlbum',
'c10': 'strArtist',
'c11': 'strGenre',
'c12': 'strTrack',
'c13': 'strUnknown1',
'c14': 'strUnknown2',
'c15': 'strUnknown3',
'c16': 'strUnknown4',
'c17': 'strUnknown5',
'c18': 'strUnknown6',
'c19': 'strUnknown7',
'c20': 'strUnknown8',
'c21': 'strUnknown9',
'c22': 'strUnknown10',
'c23': 'strUnknown11',
}
episode_schema_map = {
'c00': 'strTitle',
'c01': 'strPlot',
'c02': 'strRatingVotes',
'c03': 'strRating',
'c04': 'strRatingVotes',
'c05': 'strFirstAired',
'c06': 'strThumb',
'c07': 'strUnknown1',
'c08': 'strWatched',
'c09': 'strRuntime',
'c10': 'strDirector',
'c11': 'strUnknown2',
'c12': 'strSeasonNum',
'c13': 'strEpisodeNum',
'c14': 'strOriginalTitle',
'c15': 'strSortSeason',
'c16': 'strSortEpisode',
'c17': 'strBookmark',
'c18': 'strUnused1',
'c19': 'strUnused2',
'c20': 'strUnused3'
}

movie_schema_map = {
'c00': 'strTitle',
'c01': 'strPlot',
'c02': 'strPlotOutline',
'c03': 'strTagline',
'c04': 'strRatingVotes',
'c05': 'strRating',
'c06': 'strWriters',
'c07': 'strYear',
'c08': 'strThumbs',
'c09': 'strIMDBID',
'c10': 'strSortTitle',
'c11': 'strRuntime',
'c12': 'strMPAA',
'c13': 'strTop250',
'c14': 'strGenre',
'c15': 'strDirector',
'c16': 'strOriginalTitle',
'c17': 'strUnknown',
'c18': 'strStudio',
'c19': 'strTrailer',
'c20': 'strFanart',
'c21': 'strCountry',
'c22': 'strFileName',
'c23': 'idPath'
}

tvshow_schema_map = {
'c00': 'strTitle',
'c01': 'strPlot',
'co2': 'strStatus',
'c03': 'strVotes',
'c04': 'strRating',
'c05': 'strFirstAired',
'c06': 'strThumb',
'c07': 'strUnknown1',
'c08': 'strGenre',
'c09': 'strOriginalTitle',
'c10': 'strEpisodeGuide',
'c11': 'strFanart',
'c12': 'strSeriesID',
'c13': 'strContentRating',
'c14': 'strNetwork',
'c15': 'strSortTitle',
'c16': 'strPath2',
'c17': 'idPath',
'c18': 'strUnknown4',
'c19': 'strUnknown5',
'c20': 'strUnknown6',
'c21': 'strUnknown7',
'c23': 'strUnknown8'
}

""" SQLObject class for movies wanted table """
class MoviesWanted(SQLObject):
    strImdb = StringCol()
    strTmdb = StringCol()
    strFanart = StringCol()
    strThumb = StringCol()
    strPlot = StringCol()
    strTitle = StringCol()
    strRating = StringCol()
    strYear = StringCol()
    strGenre = StringCol()

""" SQLObject class for movie table """
class Movie(SQLObject):
    strLastPlayed = StringCol()
    idSet = IntCol()
    idMovie = IntCol()
    idFile = IntCol()
    playCount = IntCol()
    totalTimeInSeconds = StringCol()
    strSet = StringCol()
    strTrailer = StringCol()
    strStudio = StringCol()
    strTop250 = StringCol()
    strMPAA = StringCol()
    strRuntime = StringCol()
    strSortTitle = StringCol()
    strRuntime = StringCol()
    strUnknown = StringCol()
    strOriginalTitle = StringCol()
    strDirector = StringCol()
    strGenre = StringCol()
    dateAdded = StringCol()
    strFileName = StringCol()
    strPath = StringCol()
    strFileName = StringCol()
    idPath = StringCol()
    strFanart = StringCol()
    strCountry = StringCol()
    strThumb = StringCol()
    strIMDBID = StringCol()
    strTitle = StringCol()
    strPlot = StringCol()
    strPlotOutline = StringCol()
    strTagline = StringCol()
    strRatingVotes = StringCol()
    strRating = StringCol()
    strWriters = StringCol()
    strYear = StringCol()    

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
    iImage = IntCol()
    iFanart = IntCol()
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

""" SQLObject class for stream_details table """
class StreamDetails(SQLObject): 
    iStreamType = IntCol()
    iVideoWidth = IntCol()
    iVideoHeight = IntCol()
    iAudioChannels = IntCol()
    iVideoDuration = IntCol()
    fVideoAspect = FloatCol()
    strVideoCodec = StringCol()
    strAudioCodec = StringCol()
    strAudioLanguage = StringCol()
    strSubtitleLanguage = StringCol()

""" SQLObject class for video_art table """
class VideoArt(SQLObject): 
    media_id = IntCol()
    media_type = StringCol()
    type = StringCol()
    url = StringCol()   

""" SQLObject class for tv_show table """
class TvShow(SQLObject): 
     idShow = IntCol()
     strContentRating = StringCol()
     totalSeasons = IntCol()
     watchedcount = IntCol()
     lastPlayed = StringCol()
     strTitle = StringCol()
     strSeriesID= StringCol()   
     strFanart = StringCol()
     strEpisodeGuide = StringCol()
     strPath = StringCol()   
     strPath2 = StringCol()   
     idPath= StringCol()   
     strUnknown1 = StringCol()
     strUnknown4 = StringCol()
     strUnknown5 = StringCol()
     strUnknown6 = StringCol()
     strUnknown7 = StringCol()
     strUnknown8 = StringCol()
     strSortTitle = StringCol()
     strNetwork = StringCol()   
     strGenre = StringCol()
     strOriginalTitle = StringCol()
     strPlot= StringCol()   
     strStatus = StringCol()
     strVotes = StringCol()
     strRating = StringCol()   
     strFirstAired = StringCol()
     strThumb = StringCol()

    
class Manager:
    def __init__(self):
        """ Add module to list of modules on load and set required settings """
        self.logger = logging.getLogger('modules.manager')
        Monitor(cherrypy.engine, scheduler.schedule, frequency=30).subscribe()
        Album.createTable(ifNotExists=True)
        Discography.createTable(ifNotExists=True)
        Artist.createTable(ifNotExists=True)
        Song.createTable(ifNotExists=True)
        MusicArt.createTable(ifNotExists=True)
        VideoArt.createTable(ifNotExists=True)
        Movie.createTable(ifNotExists=True)
        MoviesWanted.createTable(ifNotExists=True)
        TvShow.createTable(ifNotExists=True)
        pytunes.MODULES.append({
            'name': 'Media Manager',
            'id': 'manager',
            'fields': [
                {'type':'bool', 
                    'label':'Enable', 
                    'name':'manager_enable'},
                {'type':'text', 
                    'label':'Menu name', 
                    'name':'manager_name'},
                {'type':'text', 
                    'label':'Movie Source Folder', 
                    'name':'movie_in',
                    'desc':'Where Movies Are Downloaded', 
                    'dir':True},
                {'type':'text', 
                    'label':'Movie Destination Folder', 
                    'name':'movie_out', 
                    'dir':True},
                {'type':'text', 
                    'label':'Music Source Folder', 
                    'name':'music_in', 
                    'desc':'Where Music is Downloaded', 
                    'dir':True},
                {'type':'text', 
                    'label':'Music Destination Folder', 
                    'name':'music_out', 
                    'dir':True},
                {'type':'text', 
                    'label':'Fanart.tv Apikey', 
                    'name':'fatv_apikey'},
                {'type':'bool', 
                    'label':'Fanart.tv Use SSL', 
                    'name':'fatv_ssl'},
                {'type':'text', 
                    'label':'Last.fm Apikey', 
                    'name':'lastfm_apikey'},
                {'type':'text', 
                    'label':'Last.fm Secret Key', 
                    'name':'lastfm_secretkey'},
                {'type':'bool', 
                    'label':'Last.fm Use SSL', 
                    'name':'lastfm_ssl'},
                {'type':'text', 
                    'label':'TMDB Apikey', 
                    'name':'tmdb_apikey'},
                {'type':'bool', 
                    'label':'TMDB Use SSL', 
                    'name':'tmdb_ssl'}
        ]})


    @cherrypy.expose()
    def index(self):
        """ Generate page from template """
        return pytunes.LOOKUP.get_template('manager.html').render(scriptname='manager')

    @cherrypy.expose()
    def FindMovie(self, tmdbid):
        """ Add Movie To Wanted DB Table """
        info = tmdb.MovieInfo(tmdbid)
        if info:
            if info['fanart']:
                fanart = info['fanart'][0]
            else: 
                fanart = ''
            if info['posters']:
                poster = info['posters'][0]
            else: 
                poster = ''
        #Check to see if it's already in the table
        try:
            check = MoviesWanted.selectBy(strTmdb=tmdbid).getOne()
            if check:
                return 'Already in the Want List'
        except SQLObjectNotFound:
            MoviesWanted(strTmdb=tmdbid, strImdb=info['imdb'], strTitle=info['title'], strFanart=fanart, strThumb=thumb, strRating=info['rating'], strPlot=info['plot'])

    @cherrypy.expose()
    def GetMovie(self, tmdbid):
        """ Get Movie info """
        movie = {}
        directors = []
        writers = []
        genres = []
        actors = ''

        download = html('download_button') % tmdbid
        print 'tmdbid', tmdbid
        info = tmdb.MovieInfo(tmdbid)
        print 'title: ', info['title']
        print 'release_date: ', info['release_date']
        print 'trailers: ', info['trailers']
        print 'plot: ', info['plot']
        print 'popularity: ', info['popularity']
        print 'year: ', info['year']
        print 'imdb: ', info['imdb']
        print 'genre: ', info['genre']
        print 'tagline: ', info['tagline']
        print 'runtime: ', info['runtime']
        print 'original_title: ', info['original_title']
        print 'rating: ', info['rating']
        print 'country: ', info['country']
        print 'language: ', info['language']
        for each in info['directors']:
            directors.append(each['name'])
        if directors:
            directors = ", ".join(directors)
        else:
            directors = 'N/A'
        for each in info['writers']:
            writers.append(each['name'])
        if writers:
            writers = ", ".join(writers)
        else:
            writers = 'N/A'
        if info['posters']:
            poster = info['posters'][0]
        else:
            host = 'localhost' if pytunes.settings.get('app_host') == '0.0.0.0' else pytunes.settings.get('app_host')
            poster = pytunes.IMGURL + 'no_art_square.png'
        for each in info['cast']:
            shortname = (each['name'][:14] + '..') if len(each['name']) > 16 else each['name']
            shortrole = (each['role'][:14] + '..') if len(each['role']) > 16 else each['role']
            actors += html('actor_li') % (each['name'], each['role'], each['thumb'], shortname, shortrole)
        if info['trailers']:
            trailer  = html('trailer') % info['trailers'][0]
        else:
            trailer = ''
        if info['imdb']:
            imdb = html('imdb') % info['imdb']
        else:
            imdb = ''
        if info['fanart']:
            movie['fanart'] = info['fanart'][0]
        else:
            movie['fanart']  = ''
        movie['body'] = html('modal_middle') % (poster, info['plot'], directors, ", ".join(info['genre']), info['runtime'], writers, ", ".join(info['country']), ", ".join(info['studios']), actors)
        movie['head'] = info['title'] + '   ' + info['release_date']
        movie['foot'] = imdb + trailer + download + html('close_button')
        return json.dumps(movie)

        
    @cherrypy.expose()
    def GetMovies(self, offset, limit):
        """ Generate page from template """
        table = ''
        data = table_dump('video.db', 'movieview', limit, offset, 'c00')
        for movie in data:
            if movie['c19']:
                trailer = "<img src='../img/yes16.png'>"
            else:
                trailer = "<img src='../img/no16.png'>"
            if movie['c03']:
                tagline = "<img src='../img/yes16.png'>"
            else:
                tagline = "<img src='../img/no16.png'>"
            if movie['c05']:
                rating = movie['c05'][:4]
            else:
                rating = "<img src='../img/no16.png'>"
            if movie['c12']:
                mpaa = movie['c12'].replace('Rated', '')
                mpaa.strip()
                if mpaa == '':
                    mpaa = "<img src='../img/no16.png'>"
            else:
                mpaa = "<img src='../img/no16.png'>"
            if movie['c01']:
                plot = "<img src='../img/yes16.png'>"
            else:
                plot = "<img src='../img/no16.png'>"
            if movie['c15']:
                director = "<img src='../img/yes16.png'>"
            else:
                director = "<img src='../img/no16.png'>"
            if movie['c06']:
                writers = "<img src='../img/yes16.png'>"
            else:
                writers = "<img src='../img/no16.png'>"
            if movie['c14']:
                genre = "<img src='../img/yes16.png'>"
            else:
                genre = "<img src='../img/no16.png'>"
            if movie['c08']:
                thumb = "<img src='../img/yes16.png'>"
            else:
                thumb = "<img src='../img/no16.png'>"
            if movie['c20']:
                fanart = "<img src='../img/yes16.png'>"
            else:
                fanart = "<img src='../img/no16.png'>"
            title = movie['c00']
            year = movie['c07']
            imdb = movie['c09']
            duration = movie['c11']
            vcodec = "vcodec"
            quality = "quality"
            acodec = "acodec"
            channels = "channels"
            subt = "subt"
            table += html('row19') %  (title, year, vcodec, quality, acodec, channels, subt, fanart, thumb, mpaa, trailer, genre, rating, imdb, plot, tagline, director, writers, duration) 
        return table

    @cherrypy.expose()
    def RebuildDB(self, action):
        """ Generate page from template """
        if action == "movies":
            data = table_dump('video.db', 'movieview', '10', '0')
            return pytunes.LOOKUP.get_template('manager.html').render(scriptname='manager')
        if action == "tv":
            data = table_dump('video.db', 'tvshowview', '10', '0')
            data2 = table_dump('video.db', 'episodeview', '10', '0')
        if action == "music":
            data = table_dump('music.db', 'artistview', '10', '0')
            data2 = table_dump('music.db', 'albumview', '10', '0')
            data3 = table_dump('music.db', 'artistview', '10', '0')
            data4 = table_dump('music.db', 'discography', '10', '0')
        if action == "episode":
            data = table_dump('video.db', 'episodeview', '10', '0')
        if action == "musicvideo":
            data = table_dump('video.db', 'musicvideoview', '10', '0')
        if action == "art":
            data = table_dump('video.db', 'art', '10', '0')
            data2 = table_dump('music.db', 'art', '10', '0')
        return pytunes.LOOKUP.get_template('manager.html').render(scriptname='manager')

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

        template = pytunes.LOOKUP.get_template('xbmc_album.html')
        return template.render(
            scriptname=None,
            artist_id=response['album'][0]['ArtistID'],
            album_id=album_id,
            module_name=pytunes.settings.get('xbmc_name') or 'XBMC',
            album=response['album'][0],
            tracks=response['tracks'],
            description=response['description'][0],
        )

    @cherrypy.expose()
    def Tmdb(self, source, page):
        self.logger.debug("Get list of %s movies from TMDB" % source)
        if source == 'intheaters':
            data = tmdb.Nowplaying(page)
        elif source == 'releases':
            data = tmdb.Releases(page)
        elif source == 'toprated':
            data = tmdb.Toprated(page)
        elif source == 'popular':
            data = tmdb.Popular(page)
        else:
            return
        movies = ''
        #print data
        #print data['total_pages'], 'total pages'
        for each in data['results']:
            if each['poster_path']:
                thumb = 'http://image.tmdb.org/t/p/original%s' % each['poster_path']
            else:
                thumb = pytunes.IMGURL + 'no_art_square.png'
            shorttitle = (each['title'][:14] + '..') if len(each['title']) > 16 else each['title']
            movies += html('thumb_item') % (each['title'], each['id'],  thumb, shorttitle) 
        return movies

    @cherrypy.expose()
    def Carousel(self, carousel, page=1):
        self.logger.debug("Get list of movies for %s" % carousel)
        movies = ''
        if carousel == 'upcoming':
            data = tmdb.Releases(page)
        if carousel == 'toprated':
            data = tmdb.Toprated(page)
        if carousel == 'theaters':
            data = tmdb.Nowplaying(page)
        if carousel == 'popular':
            data = tmdb.Popular(page)
        for each in data['results']:
            if each['backdrop_path']:
                movies += html('carousel_item') % (each['backdrop_path'], each['title'], each['release_date']) 
        return movies

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
        template = pytunes.LOOKUP.get_template('xbmc_artist.html')
        return template.render(
            scriptname='xbmc_artist',
            artist_id=artist_id,
            name=artist
        )

    @cherrypy.expose()
    def GetThumb(self, thumb=None, h=None, w=None, o=100):
        """ Parse thumb to get the url and send to pytunes.proxy.get_image """
        if h and w:
            if int(h)/int(w) > 1.15:
                url = '../img/no_art_poster.png'
            elif int(h)/int(w) < .85:
                url = '../img/no_art_fanart'
            else:
                url = '../img/no_art_square.png'
        else:
            url = '../img/no_art_square.png'
        if thumb:
            url = thumb
            self.logger.debug("Trying to fetch image via " + url)
        return get_image(url, h, w, o, "")

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def GetShows(self, offset, limit):
        """ Get a list of all the TV Shows """
        self.logger.debug("Fetching TV Shows")
        table = ''
        data = table_dump('video.db', 'tvshowview', limit, offset, 'c00')
        for show in data:
            title = show['c00']
            year = show['c05']
            seasons = show['totalSeasons']
            #duration = show['c11']
            vcodec = "vcodec"
            quality = "quality"
            acodec = "acodec"
            channels = "channels"
            subt = "subt"
            table += html['row19'] %  (title, year, seasons, channels, subt, vcodec, quality, acodec, channels, subt, vcodec, quality, acodec, channels, subt, vcodec, quality, acodec, channels) 
        return table

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
