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
    def search(self, quality= 'ALL', limit=40, set=1, rating=0, keywords='Star Wars', genre='All', sort='date', order='desc', format='json'):
        print 'hellow'

    @cherrypy.expose()
    def newest(self, quality= 'ALL', format='json'):
        data = self.movie_list(1, 40, 'ALL', 0, '', 'ALL', 'date', 'desc', format)
        movies = ''
        for movie in data['movies']['MovieList']:
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
        #print moviedata['LargeScreenshot1']
        print 'movie', moviedata
        return json.dumps(movie)

    def upcoming(self, format='json'):
        self.uri = 'upcoming'

        data = {
            'movies':   [],
            'errors':   {
                'state':    False,
                'message':  []
            }
        }

        errors = {
            'state': False,
            'message': []
        }

        if format in self.data_formats:
            self.uri = '%s.%s' % (self.uri, format)
        else:
            errors['state'] = True
            errors['message'].append('Data return format must be json, xml or csv')

        if errors['state']:
            data['errors'] = errors
        else:
            url = self._construct_url()
            m = self._fetch_data(url)
            if m is not None:
                data['movies'] = m

        return data

    def movie_list(self,
                   set=1, limit=40,
                   quality='ALL', rating=0,
                   keywords='', genre='ALL',
                   sort='date', order='desc',
                   format='json'):
        uri = 'list'

        data = {
            'movies':   [],
            'errors':   {
                'state':    False,
                'message':  []
            }
        }

        movie_list_params = {
            'limit':            40,         # Maximum number of returned items
            'set':              1,          # Which set (page) do you want to return?
            'quality':          'ALL',      # {720p, 1080p, 3D, ALL}
            'rating':           0,          # Minimum rating between 0 - 9
            'keywords':         '',         # {String}
            'genre':            'ALL',      # {String} Refer to http://www.imdb.com/genre/
            'sort':             'date',     # {date, seeds, peers, size, alphabet, rating, downloaded, year}
            'order':            'desc'      # {desc, asc}
        }

        opt_qualities = ['720p', '1080p', '3D', 'ALL']
        opt_ratings = range(10)
        opt_sorts = ['date', 'seeds', 'size', 'alphabet', 'rating']
        opt_orders = ['desc', 'asc']

        data_formats = ['json', 'xml', 'csv']

        params = copy.deepcopy(movie_list_params)
        errors = {
            'state': False,
            'message': []
        }

        if quality in opt_qualities:
            params['quality'] = quality
        else:
            errors['state'] = True
            errors['message'].append('Quality needs to be 720p, 1080p, 3D or ALL')

        if rating in opt_ratings:
            params['rating'] = rating
        else:
            errors['state'] = True
            errors['message'].append('Rating needs to be an integer between 0 to 10')

        if sort in opt_sorts:
            params['sort'] = sort
        else:
            errors['state'] = True
            errors['message'].append('Sort needs to be date, seeds, size, alphabet or rating')

        if order in opt_orders:
            params['order'] = order
        else:
            errors['state'] = True
            errors['message'].append('Order needs to be desc or asc')

        if format in data_formats:
            uri = '%s.%s' % (uri, format)
        else:
            errors['state'] = True
            errors['message'].append('Data return format must be json, xml or csv')

        if errors['state']:
            data['errors'] = errors
        else:
            url = self._construct_url(uri)
            m = self._fetch_data(url)
            if m is not None:
                data['movies'] = m

        return data

    def _fetch_data(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            #print r.text
            return json.loads(r.text)
        else:
            return None

    def _construct_url(self, uri):
        base_url = 'https://yts.re/api/'
        return "%s%s" % (base_url, uri)

    class client:
        def waku(self):
            return "waku"
