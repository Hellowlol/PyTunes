import htpc
from tmdbsimple import TMDB
tmdb = TMDB(htpc.settings.get('tmdb_apikey', ''))
tmdb_url = 'http://image.tmdb.org/t/p/original'

def MovieInfo(tmdbid):
    movie = tmdb.Movies(tmdbid)
    stuff = movie
    print stuff
    return movie.info(), movie.images(), movie.trailers(), movie.people()
    #print response
    #response = movie.images()
    #print response
    #response = movie.trailers()
    #print response

def Search(query, type):
    if type == 'movie':
        search = tmdb.Search()
        return search.movie({'query':query})





