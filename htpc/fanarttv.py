import os
import htpc
from fanart.movie import Movie
fatv_apikey = htpc.settings.get('fatv_apikey', '')
os.environ.setdefault('FANART_APIKEY', fatv_apikey)
fanart, arts, discs, banners, logos, hdlogos, posters, thumbs = [], [], [], [], [], [], [], []
def GetArt(id, type):
    if type == 'movie': 
        try:               
            movie = Movie.get(id)
        except:
            print 'error connecting to fanart.tv'
            return {}
        for item in movie.backgrounds:
            fanart.append(item.url)
        for item in movie.arts:
            arts.append(item.url)
        for item in movie.discs:
            discs.append(item.url)
        for item in movie.banners:
             banners.append(item.url)
        for item in movie.logos:
            logos.append(item.url)
        for item in movie.hdlogos:
            hdlogos.append(item.url)
        for item in movie.posters:
            posters.append(item.url)
        for item in movie.thumbs:
            thumbs.append(item.url)

    return {'fanart':fanart, 'arts':arts, 'discs':discs, 'banners':banners, 'logos':logos, 'hdlogos':hdlogos, 'posters':posters, 'thumbs':thumbs}

