import pytunes
import xdb
import logging
import guessit
import urllib
from json import loads
from engines import ka
settings = pytunes.settings
logger = logging.getLogger('searcher')
def FindMovies():
    movies = xdb.table_dump('database.db', 'movies_wanted', 10, 0, 'str_title')
    for movie in movies:
        #search nzb by imdb or title?
        #search kickasstorrents by title, year and category 
        results =  ka.search(urllib.quote('%s %s' % (movie['str_title'], movie['str_year'])), 'movies')
        if results:
            for result in results:
                languages = []
                guess = guessit.guess_movie_info(result['name'])
                #print guess
                if 'videoCodec' in guess:
                    vcodec = guess['videoCodec']
                else:
                    vcodec = 'Unknown'
                if 'audioCodec' in guess:
                    acodec = guess['audioCodec']
                else:
                    acodec = 'Unknown'
                if 'year' in guess:
                    year = guess['year']
                else:
                    year = ''
                if 'title' in guess:
                    title = guess['title']
                else:
                    pass
                if 'screensize' in guess:
                    screensize = guess['sreensize']
                else:
                    screensize = 'Unknown'
                if 'releaseGroup' in guess:
                    rgroup = guess['releaseGroup']
                else:
                    rgroup = ''
                if 'format' in guess:
                    format = guess['format']
                else:
                    format = ''
                if 'other' in guess:
                    other = ", ".join(guess['other'])
                else:
                    other = ''
                if 'size' in result:
                    size = result['size']
                else:
                    size = ''
                if 'language' in guess:
                    for each in guess['language']:
                        languages.append(each.english_name)
                    language = ", ".join(languages)
                else:
                    language = 'Unknown'
                if 'container' in guess:
                    container = guess['container']
                else:
                    container = 'Unknown'
                print title, year, format, screensize, language,  rgroup, vcodec, acodec, container, size
        else: 
            print 'No results for %s movie' % movie['str_title']
            #results =  ka.search(movie['str_title'], 'movies')
            #search yify by title
            #print results
def fetch(self, cmd):
    try:
        settings = pytunes.settings
        host = settings.get('newznab_host', '').replace('http://', '').replace('https://', '')
        ssl = 's' if settings.get('newznab_ssl', 0) else ''
        apikey = settings.get('newznab_apikey', '')
        url = 'http%s://%s/api?o=json&apikey=%s&t=%s' % (ssl, host, apikey, cmd)
        self.logger.debug("Fetching information from: %s" % url)
        return loads(urlopen(url, timeout=10).read())
    except:
        self.logger.error("Unable to fetch information from: %s" % url)
        return

