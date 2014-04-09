from datetime import datetime
from mako.template import Template
import guessit
import glob
import urllib
import os
import string
import htpc
import staticvars
import enzyme
import tmdb
import fanarttv

def stripall(str):
    str = ''.join(ch for ch in str if ch not in exclude)
    str = str.strip()
    str = str.lower()
    str = str.replace(' ', '')
    return str

def names(movie, stream):
    filename = []
    dirname = movie['title']
    title = movie['title'].lower()
    title = title.split(' ')
    title = '.'.join(title)
    filename.append(title)
    dirname += ' (' + str(movie['year']) + ')'
    filename.append('.' + str(movie['year']))
    if 'width' in stream:
        if stream['width'] == '720':
            filename.append('.' + '720p')
            dirname += ' [720p]'
        if stream['width'] == '1080':
            filename.append('.' + '1080p')
        filename.append('.' + 'BluRay')
    elif movie['screenSize']:
        filename.append('.' + movie['screenSize'])
        dirname += ' [' + movie['screenSize'] + ']'
        if movie['format']:
            filename.append('.' + movie['format'])
        else:
            if movie['screenSize'] == '720p' or movie['screenSize'] == '1080p':
                filename.append('.' + 'BluRay')
    filename.append('.' + movie['container'])
    filename = ''.join(filename)
    return filename, dirname

def buildnfo(destdir, info, stream):
    nfo = Template(staticvars.get_var('movienfo'))
    #print nfo.render(info)
    return

def procpics(destdir, info):
    print 'in procpics'
    return ''

def mergeart(info, fa):
    #print info, fa
    info['discs'] = fa['discs']
    info['arts'] = fa['arts']
    info['banners'] = fa['banners']
    info['logos'] = fa['logos']
    info['hdlogos'] = fa['hdlogos']
    info['posters'].extend(fa['posters'])
    info['fanart'].extend(fa['fanart'])
    info['thumbs'] = fa['thumbs']
    return info

def download(url, dest):
    urllib.urlretrieve (url, dest)

def streaminfo(file):
    try:
        info = enzyme.parse(file)
    except:
        print 'Error Detecting Streams: ', file
        return 'Enzyme error'
    movieinfo = {
        'length':'',
        'vcodec':'',
        'acodec':'',
        'height':'',
        'width':'',
        'aspect':'',
        'samplerate':'',
        'channels':''}
    info = str(info)
    lines =  info.split('+--')
    head = lines[0].split('\n')
    video = lines[1].split('\n')
    audio = lines[2].split('\n')

    for line in head:
        if 'length' in line:
            movieinfo['length'] = line.split(':')[1].strip()
    for line in video:
        if 'codec' in line and not 'codec_' in line:
            movieinfo['vcodec'] = line.split(':')[1].strip()
        if 'width' in line:
            movieinfo['width'] = line.split(':')[1].strip()
        if 'height' in line:
            movieinfo['height'] = line.split(':')[1].strip()
        if 'aspect' in line:
            movieinfo['aspect'] = line.split(':')[1].strip()
    for line in audio:
        if 'codec' in line and not 'codec_' in line:
            movieinfo['acodec'] = line.split(':')[1].split()
        if 'channels' in line:
            movieinfo['channels'] = line.split(':')[1].strip()
        if 'samplerate' in line:
            movieinfo['samplerate'] = line.split(':')[1].strip()
    return movieinfo

def process():
    #print 'in proccess'
    moviedir = htpc.settings.get('movie_in', '')
    destdir = htpc.settings.get('movie_out', '')
    total = 0
    hits = 0 
    moviepath = ''
    matched = []  
    unmatched = []  
    exclude = ['\'', '"', '-', ';', ':']
    if not os.path.exists(moviedir):
        os.makedirs(moviedir)
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    if not os.access(destdir, os.W_OK):
        sys.exit("No write access to destination movie folder")
    if not (moviedir.endswith('/')):
        moviedir += '/'
    if not (destdir.endswith('/')):
        destdir += '/'
    paths = glob.glob(moviedir + '*')
    #print 'paths', paths
    for path in paths:
        match = 0
        matches = {}
        if not os.path.isfile(path):
              continue
        moviepath = path    
        file = os.path.basename(path)
        print file
        guess = guessit.guess_movie_info(file, info = ['filename'])
        mimetype, container, screenSize, videoCodec, format = '', '', '', '', ''
        if 'mimetype' in guess:
            mimetype = guess['mimetype']
        if 'container' in guess:
            container = guess['container']
        if 'screenSize' in guess:
            screenSize = guess['screenSize']
        if 'videoCodec' in guess:
            videoCodec = guess['videoCodec']
        if 'format' in guess:
            format = guess['format']
        search = tmdb.Search(guess['title'], 'movie')
        total += 1
        for s in search['results']:
            if  'year' in guess:
                if str(guess['year']) in s['release_date']:
                    match += 1
                    matches[match] = [s['title'], s['id'], s['release_date'], mimetype, container, screenSize, videoCodec, format]
                else:
                    if len(search.results) == 1:
                        match += 1
                        matches[match] = [s['title'], s['id'], s['release_date'], mimetype, container, screenSize, videoCodec, format]
                    else:
                        stripguess = stripall(str(guess['title']))
                        stripsearch = stripall(s['title'])
                        if stripguess == stripsearch:
                            match += 1
                            matches[match] = [s['title'], s['id'], s['release_date'], mimetype, container, screenSize, videoCodec, format]

            else:
                stripguess = stripall(str(guess['title']))
                stripsearch = stripall(s['title'])
                if stripguess == stripsearch:
                    match += 1
                    matches[match] = [s['title'], s['id'], s['release_date'], mimetype, container, screenSize, videoCodec, format]

        if not matches and search.results:
            unmatched.append(guess['title'])
        if len(matches) == 1:
            dt = datetime.strptime(matches[1][2], '%Y-%m-%d')
            matched.append({'title':matches[1][0], 'tmdbid':matches[1][1], 'path':moviepath, 'year':dt.year, 'mimetype':matches[1][3], 'container':matches[1][4], 'screenSize':matches[1][5], 'videoCodec':matches[1][6], 'format':matches[1][7]})
            hits += 1
        if len(matches) > 1:
            testguess = stripall(guess['title'])
            for each in matches:
                testeach = stripall(matches[each][0])
                if testeach == testguess:
                    dt = datetime.strptime(matches[each][2], '%Y-%m-%d')
                    matched.append({'title':matches[each][0], 'tmdbid':matches[each][1], 'path':moviepath, 'year':dt.year, 'mimetype':matches[each][3], 'container':matches[each][4], 'screenSize':matches[each][5], 'videoCodec':matches[each][6], 'format':matches[each][7]})
                    hits += 1
                    break
                else:
                    unmatched.append(guess['title'])
    for movie in matched:
        stream = streaminfo(movie['path'])
        #print stream
        filename, dirname = names(movie, stream)
        if not os.path.exists(destdir + dirname):
            os.makedirs(destdir + dirname)
        info = tmdb.MovieInfo(movie['tmdbid'])
        fa_art = fanarttv.GetArt(movie['tmdbid'], 'movie')
        if fa_art:
            info = mergeart(info, fa_art)
        print info
        print filename,dirname
        procpics(destdir, info) 
        buildnfo(destdir, info, stream)

