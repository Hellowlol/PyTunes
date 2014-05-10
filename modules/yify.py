import pytunes
from pytunes.staticvars import get_var as html
import cherrypy
import logging
import requests, copy, json

class Yify:
    def __init__(self):
        self.logger = logging.getLogger('modules.yify')
        pytunes.MODULES.append({
            'name': 'YIFY Search',
            'id': 'yify',
            'fields': [
                {'type':'bool', 'label':'Enable', 'name':'yify_enable'},
                {'type':'text', 'label':'Menu name', 'name':'yify_name'}
        ]})

    @cherrypy.expose()
    def index(self, query='', **kwargs):
        return pytunes.LOOKUP.get_template('yify.html').render(scriptname='yify')

    @cherrypy.expose()
    def search(self, quality= 'ALL', limit=40, set=1, rating=0, keywords='', genre='All', sort='date', order='desc'):
        #print 'hellow, come to the Dark side. You must complete your journey, weedhopper.'
        url = html('yify_link') % (limit, set, quality, rating, keywords, genre, sort, order)
        movies = ''
        moviedata = self._fetch_data(url)
        for movie in moviedata['MovieList']:
            title = (movie['MovieTitleClean'][:14] + '..') if len(movie['MovieTitleClean']) > 16 else movie['MovieTitleClean']
            title += '<br>' + movie['MovieYear']
            movies += html('yify_thumb_item') % (movie['MovieTitle'], movie['MovieID'],  movie['CoverImage'], title) 
        return movies

    @cherrypy.expose()
    def GetMovie(self, yifyid):
        format='json'
        directors = []
        actors = []
        genres = []
        print 'get movie id: ', yifyid
        url = 'https://yts.re/api/movie.json?id=%s' % yifyid
        movie = {}
        moviedata = self._fetch_data(url)
        if 'YoutubeTrailerID' in moviedata:
            trailer = html('trailer') % moviedata['YoutubeTrailerID']
        else:
            trailer = ''
        if 'ImdbCode' in moviedata:
            imdb = html('imdb') % moviedata['ImdbCode']
        else:
            imdb = ''
        for each in moviedata['DirectorList']:
            directors.append(each['DirectorName'])
        director = ", ".join(directors)
        for each in moviedata['CastList']:
            actors.append(html('actor_imdb') % (each['ActorImdbCode'], each['ActorName'], each['CharacterName'], each['ActorName']))
        actor = ", ".join(actors)
        if 'Genre1' in moviedata:
            if moviedata['Genre1']:
                genres.append(moviedata['Genre1'])
        if 'Genre2' in moviedata:
            if moviedata['Genre2']:
                genres.append(moviedata['Genre2'])
        if 'Genre3' in moviedata:
            if moviedata['Genre3']:
                genres.append(moviedata['Genre3'])
        if genres:
            genre = ", ".join(genres)
        else:
            genre = 'N/A'

        movie['head'] = moviedata['MovieTitle']
        movie['body'] = html('yify_modal_middle') % (moviedata['LargeCover'], moviedata['LongDescription'], director, genre, moviedata['MovieRating'], moviedata['MovieRuntime'], moviedata['AgeRating'], actor, moviedata['Size'], moviedata['TorrentSeeds'], moviedata['Language'])

        download = html('torrent_button') % moviedata['TorrentUrl']        
        movie['foot'] = imdb + trailer + download + html('close_button')
        movie['fanart'] = moviedata['LargeScreenshot1']
        #print 'movie', moviedata
        return json.dumps(movie)

    def _fetch_data(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            return None

    class client:
        def waku(self):
            return "waku"
