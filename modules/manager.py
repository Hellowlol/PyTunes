#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Module for Media Management  """
import cherrypy
import pytunes
from qbittorrent import qbittorrent as qb
from pytunes import tmdb, staticvars, scheduler, processmovies, processtv, processmusic, searcher, imdbpy
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
from random import randint
from apscheduler.scheduler import Scheduler
from cherrypy.lib.auth2 import require
sched = Scheduler()
sched.start() 
settings = pytunes.settings

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
    strRuntime = StringCol()
    strStudios = StringCol()
    strCountry = StringCol()
    strWriters = StringCol()
    strDirectors = StringCol()
    strActors = StringCol()


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
        Monitor(cherrypy.engine, processmovies.process, frequency=90).subscribe()
        #job1 = sched.add_cron_job(processmovies.process, minute="*/%s" % 15)
        #job2 = sched.add_cron_job(processtv.process, minute="*/%s" % 15)
        #job3 = sched.add_cron_job(processmusic.process, minute=randint(0,59))
        #job4 = sched.add_cron_job(searcher.FindMovies, minute="*/%s" % 5)
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
                    'dir':False},
                {'type':'text', 
                    'label':'Movie Destination Folder', 
                    'name':'movie_out', 
                    'dir':False},
                {'type':'text', 
                    'label':'Music Source Folder', 
                    'name':'music_in', 
                    'desc':'Where Music is Downloaded', 
                    'dir':False},
                {'type':'text', 
                    'label':'Music Destination Folder', 
                    'name':'music_out', 
                    'dir':True}
        ]})


    @cherrypy.expose()
    @require()
    def index(self):
        """ Generate page from template """
        return pytunes.LOOKUP.get_template('manager.html').render(scriptname='manager')


    @cherrypy.expose()
    @require()
    def GetTVShow(self, tmdbid):
        """ Get Movie info """
        show = {}
        networks = []
        languages = []
        directors = []
        writers = []
        genres = []
        actors = ''

        info = tmdb.TVInfo(tmdbid)
        addshow = html('addshow_button') % info['name']
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
            writers = ('%s..' % writers[:40]) if len(writers) > 42 else writers
        else:
            writers = 'N/A'
        for each in info['cast']:
            if each['thumb']:
                thumb = each['thumb']
            else:
                thumb = '%sno_art_square.png' % pytunes.IMGURL
            shortname = ('%s..' % each['name'][:14]) if len(each['name']) > 16 else each['name']
            shortrole = ('%s..' % each['role'][:14]) if len(each['role']) > 16 else each['role']
            actors += html('actor_li') % (each['name'], each['role'], thumb, shortname, shortrole)
        show['fanart'] = info['fanart']
        show['body'] = html('tmdb_tv_modal_middle') % (info['poster'], info['plot'], directors, info['genre'], info['status'], info['first_air'], info['last_air'], writers, info['country'], info['networks'], info['seasons'], info['episodes'], actors)
        show['head'] = '%s   %s' % (info['name'], info['first_air'])
        show['foot'] = addshow + html('close_button')
        return json.dumps(show)

    @cherrypy.expose()
    @require()
    def AddMovie(self, tmdbid='', imdbid='', year='', title='', fanart='', thumb='', plot='', rating='', genre='', runtime='', writers='', country='', studios='', actors='', directors=''):
        self.logger.debug("Saving wanted movie to the database: %s" % title)
        try:
            movie = MoviesWanted.selectBy(strTmdb=tmdbid).getOne()
            self.logger.debug('Movie already in database: %s' % title)
            msg = 'Movie already in database: %s' % title
        except SQLObjectNotFound:
            MoviesWanted(strYear=year, strTmdb=tmdbid, strImdb=imdbid, strTitle=title.encode('utf-8'), strFanart=fanart, strThumb=thumb, strPlot=plot.encode('utf-8'), strRating=rating, strGenre=genre, strRuntime=runtime, strWriters=writers.encode('utf-8'), strCountry=country.encode('utf-8'), strStudios=studios.encode('utf-8'), strActors=actors.encode('utf-8'), strDirectors=directors.encode('utf-8'))
            self.logger.debug('Movie added to wanted database: %s' % title)
            msg = 'Movie added to wanted database: %s' % title

        return msg
        
    @cherrypy.expose()
    @require()
    def WantedMovies(self):
        """ Get Wanted Movie info for interface """
        movies = ''
        for movie in MoviesWanted.select():
            if movie.strThumb:
                thumb = 'http://image.tmdb.org/t/p/original%s' % movie.strThumb
            else:
                thumb = '%sno_art_square.png' % pytunes.IMGURL
            shorttitle = ('%s..' % movie.strTitle[:14]) if len(movie.strTitle) > 16 else movie.strTitle[:14]
            shorttitle += '%s<br>' % movie.strYear
            movies += html('tmdb_thumb_item') % (movie.strTitle, movie.strTmdb,  thumb, shorttitle) 
        return movies
        
    @cherrypy.expose()
    @require()
    def Top250Movies(self):
        """ Get top 250 Movie info for interface """
        movies = imdb.Top250()
        for movie in movies:
            if movie['thumb']:
                thumb = movie['thumb']
            else:
                thumb = pytunes.IMGURL + 'no_art_square.png'
            shorttitle = ('%s..' % movie['title'][:14]) if len(movie['title']) > 16 else movie['title'][:14]
            shorttitle += '<br>%s' % movie['year']
            movies += html('tmdb_thumb_item') % (movie['title'], movie['imdbid'],  thumb, shorttitle) 
        return movies
        
    @cherrypy.expose()

    def GetMovie(self, tmdbid, page=''):
        """ Get Movie info """
        movie = {}
        directors = []
        writers = []
        genres = []
        wactors = []
        actors = ''

        info = tmdb.MovieInfo(tmdbid)
        print info
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
            wposter = info['posters'][0]
        else:
            poster = '%sno_art_square.png' % pytunes.IMGURL
            wposter = ''
        for each in info['cast']:
            if each['thumb']:
                thumb = each['thumb']
            else:
                thumb = '%sno_art_square.png' % pytunes.IMGURL
            shortname = ('%s..' % each['name'][:14]) if len(each['name']) > 16 else each['name']
            shortrole = ('%s..' % each['role'][:14]) if len(each['role']) > 16 else each['role']
            actors += html('actor_li') % (each['name'], each['role'], thumb, shortname, shortrole)
            wactors.append(each['name'])
        if info['trailers']:
            trailer  = html('trailer_button') % info['trailers'][0]
            wtrailer = info['trailers'][0]
        else:
            trailer = ''
            wtrailer = ''
        if info['imdb']:
            imdb = html('imdb') % info['imdb']
        else:
            imdb = ''
            download = html('download_button') % (tmdbid, imdb, info['title'], info['year'])
        if info['fanart']:
            movie['fanart'] = info['fanart'][0]
        else:
            movie['fanart']  = ''
        download = html('download_button') % (tmdbid, info['imdb'], info['title'], info['year'], movie['fanart'], wposter, info['plot'].replace("\"", "'"), 'rating', ", ".join(info['genre']), info['runtime'], writers, ", ".join(info['country']), ", ".join(info['studios']), ", ".join(wactors), directors)
        movie['body'] = html('tmdb_movie_modal_middle') % (poster, info['plot'], directors, ", ".join(info['genre']), info['runtime'], writers, ", ".join(info['country']), ", ".join(info['studios']), actors)
        movie['head'] = '%s   %s' % (info['title'], info['release_date'])
        if page == 'wantedmovie':
            movie['foot'] = imdb + trailer + remove + html('close_button')
        else:
            movie['foot'] = imdb + trailer + download + html('close_button')
        return json.dumps(movie)

        
    @cherrypy.expose()
    @require()
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
    @require()
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
    @require()
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
    @require()
    def Tmdb(self, source, page):
        self.logger.debug("Get list of %s movies from TMDB" % source)
        moviecats = ['intheaters', 'releases', 'toprated', 'popular']
        tvcats = ['topratedtv', 'populartv']
        if source == 'intheaters':
            data = tmdb.Nowplaying(page)
        elif source == 'releases':
            data = tmdb.Releases(page)
        elif source == 'toprated':
            data = tmdb.Toprated(page)
        elif source == 'popular':
            data = tmdb.Popular(page)
        elif source == 'topratedtv':
            data = tmdb.TopratedTV(page)
        elif source == 'populartv':
            data = tmdb.PopularTV(page)
        else:
            return
        movies = ''
        if source in moviecats:
            for each in data['results']:
                if each['poster_path']:
                    thumb = 'http://image.tmdb.org/t/p/original%s' % each['poster_path']
                else:
                    thumb = '%sno_art_square.png' % pytunes.IMGURL
                shorttitle = ('%s..' % each['title'][:14]) if len(each['title']) > 16 else each['title']
                shorttitle += '<br>%s' % each['release_date']
                movies += html('tmdb_thumb_item') % (each['title'], each['id'],  thumb, shorttitle) 
        elif source in tvcats:
            for each in data['results']:
                if each['poster_path']:
                    thumb = 'http://image.tmdb.org/t/p/original%s' % each['poster_path']
                else:
                    thumb = '%sno_art_square.png' % pytunes.IMGURL
                shortname = ('%s..' % each['name'][:14]) if len(each['name']) > 16 else each['name']
                if each['first_air_date']:
                    shortname += '<br>%s' % each['first_air_date']
                movies += html('tmdb_thumb_item') % (each['name'], each['id'],  thumb, shortname) 
        return movies

    @cherrypy.expose()
    @require()
    def Carousel(self, carousel, page=1):
        limit = 1
        self.logger.debug("Get list of movies for %s" % carousel)
        moviecats = ['theaters', 'upcoming', 'toprated', 'popular']
        tvcats = ['topratedtv', 'populartv']
        movies = ''
        if carousel == 'upcoming':
            data = tmdb.Releases(page)
        if carousel == 'toprated':
            data = tmdb.Toprated(page)
        if carousel == 'theaters':
            data = tmdb.Nowplaying(page)
        if carousel == 'popular':
            data = tmdb.Popular(page)
        if carousel == 'topratedtv':
            data = tmdb.TopratedTV(page)
        if carousel == 'populartv':
            data = tmdb.PopularTV(page)
        for each in data['results']:
            if limit >=5:
                pass
            if carousel in moviecats:
                if each['backdrop_path']:
                    movies += html('carousel_item') % (each['backdrop_path'], each['title'], each['release_date']) 
                    limit += 1
            elif carousel in tvcats:
                if each['backdrop_path']:
                    movies += html('carousel_item') % (each['backdrop_path'], each['name'], each['first_air_date']) 
                    limit += 1
        return movies

    @cherrypy.expose()
    @require()
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
            self.logger.debug("Trying to fetch image via %s" % url)
        return get_image(url, h, w, o, "")


