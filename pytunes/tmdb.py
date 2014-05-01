import pytunes
from datetime import datetime
from tmdbsimple import TMDB
tmdb = TMDB(pytunes.settings.get('tmdb_apikey', ''))
tmdb_url = 'http://image.tmdb.org/t/p/original'

def MovieInfo(tmdbid):
    fanart = [] 
    posters = []
    trailers = ''
    genres = []
    actors = []
    writers = []
    producers = []
    directors = []
    country = []
    language = []
    movie = tmdb.Movies(tmdbid)
    response = movie.trailers()
    for each in response['youtube']:
        trailers += '    <trailer>plugin://plugin.video.youtube/?action=play_video&amp;videoid=' + each['source'] + '</trailer>\n'
    if len(trailers) == 0:
        trailers += '    <trailer></trailer>\n'
    #print 'trailers     ', response
    response = movie.images()
    for each in response['backdrops']:
        fanart.append(tmdb_url + each['file_path'])
    for each in response['posters']:
        posters.append(tmdb_url + each['file_path'])
    response = movie.credits()
    for cast in response['cast']:
        if cast['profile_path']:
            thumb = tmdb_url + cast['profile_path']
        else:
            thumb = ''
        actor = {'name':cast['name'], 'role':cast['character'], 'thumb':thumb}
        actors.append(actor)
    for crew in response['crew']:
        if crew['department'] == 'Directing':
            if crew['profile_path']:
                thumb = tmdb_url + crew['profile_path']
            else:
                thumb = ''
            directors.append({'name':crew['name'], 'thumb':thumb})
        if crew['department'] == 'Writing':
            if crew['profile_path']:
                thumb = tmdb_url + crew['profile_path']
            else:
                thumb = ''
            writers.append({'name':crew['name'], 'thumb':thumb})
        if crew['department'] == 'Production':
            if crew['profile_path']:
                thumb = tmdb_url + crew['profile_path']
            else:
                thumb = ''
            producers.append({'name':crew['name'], 'thumb':thumb})
    #print directors, writers, producers
    movie_info = movie.info()
    for countries in movie_info['production_countries']:
        country.append(countries['name'])
    #for languages in movie_info['spoken_languages']:
    #    language.append(countries['name'])
    #print movie_info
    dt = datetime.strptime(movie_info['release_date'], '%Y-%m-%d')
    info = {
        'discs':[],
        'arts':[],
        'banners':[],
        'logos':[],
        'hdlogos':[],
        'thumbs':[],
        'plot':movie_info['overview'],
        'vote_count':movie_info['vote_count'],
        'imdb':movie_info['imdb_id'],
        'set':movie_info['belongs_to_collection'],#break apart
        'directors':directors,
        'writers':writers,
        'producers':producers,
        'cast':actors,
        'year':dt.year,
        'rating':movie_info['vote_average'],
        'fanart':fanart,
        'posters':posters,
        'country':country,
        'language':language,
        'trailers':trailers,
        'runtime':movie_info['runtime'],
        'tagline':movie_info['tagline'],
        'original_title':movie_info['original_title']
    }
    return info

def Search(query, type):
    if type == 'movie':
        search = tmdb.Search()
        return search.movie({'query':query})

def Releases(page):
    stuff = tmdb.Movies()
    return stuff.upcoming({'page':page})

def Nowplaying(page):
    stuff = tmdb.Movies()
    return stuff.now_playing({'page':page})

def Popular(page):
    stuff = tmdb.Movies()
    return stuff.popular({'page':page})

def Toprated(page):
    stuff = tmdb.Movies()
    return stuff.top_rated({'page':page})





