from datetime import datetime
from mako.template import Template
import guessit
import glob
import urllib
import os
import shutil
import string
import pytunes
import logging
import staticvars
import enzyme
import tmdb
import fanarttv
import os 
import time 

logger = logging.getLogger('pytunes.settings')
    
exclude = ['\'', '"', '-', ';', ':']

def stripall(str):
    str = ''.join(ch for ch in str if ch not in exclude)
    str = str.strip()
    str = str.lower()
    str = str.replace(' ', '')
    return str

def names(movie, stream):
    filename = []
    dirname = movie['title']
    title = movie['title']
    title = title.split(' ')
    title = '.'.join(title)
    filename.append(title)
    dirname += ' (%s)' % str(movie['year'])
    filename.append('.%s' % str(movie['year']))
    if 'width' in stream:
        #print 'in width', stream['width']
        if stream['width'] == '1280' or stream['height'] == '720':
            filename.append('.720p')
            dirname += ' [720p]'
            filename.append('.BlueRay')
        elif stream['width'] == '1920' or stream['height'] == '1080':
            filename.append('.1080p')
            filename.append('.BluRay')
            dirname += ' [1080p]'
        else:
            filename.append('.DVD')
            dirname += ' [DVD]'
    elif movie['screenSize']:
        filename.append('.%s' % movie['screenSize'])
        dirname += ' [%s]' % movie['screenSize']
        if movie['screenSize'] == '720p' or movie['screenSize'] == '1080p':
                filename.append('.BluRay')
        else:
            filename.append('.DVD')
            dirname += ' [DVD]'

    filename.append('.PyTunes.%s' % movie['container'])
    filename = ''.join(filename)
    filename = filename.replace('/', '-').replace('..', '.').replace(':.', '.')
    dirname = dirname.replace('/', '-')
    return filename, dirname

def buildnfo(destdir, info, stream):
    nfo = Template(staticvars.get_var('movienfo'))
    #print nfo.render(info)
    return

def procpics(destdir, info):
    if info['discs']:    
        name, ext = os.path.splitext(info['discs'][0])            
        download(info['discs'][0], '%s/discart%s' % (destdir, ext))
        if len(info['discs']) > 1:    
            i = 1
            dldir = '%s/discart' % destdir
            if not os.path.exists(dldir):
                os.makedirs(dldir)
            for each in info['discs']:
                name, ext = os.path.splitext(each)            
                download(each, '%s/discart%s%s' % (dldir, str(i), ext))
                i += 1
    if info['arts']:    
        name, ext = os.path.splitext(info['arts'][0])            
        download(info['arts'][0], '%s/clearart%s' % (destdir, ext))
        if len(info['arts']) > 1:    
            i = 1
            dldir = '%s/clearart' % destdir
            if not os.path.exists(dldir):
                os.makedirs(dldir)
            for each in info['arts']:
                name, ext = os.path.splitext(each)            
                download(each, '%s/clearart%s%s' % (dldir, str(i), ext))
                #print each
                i += 1
    if info['banners']:    
        name, ext = os.path.splitext(info['banners'][0])            
        download(info['banners'][0], '%s/banner%s' % (destdir, ext))
        if len(info['banners']) > 1:    
            i = 1
            dldir = '%s/banners' % destdir
            if not os.path.exists(dldir):
                os.makedirs(dldir)
            for each in info['banners']:
                name, ext = os.path.splitext(each)            
                download(each, '%s/banner%s%s' % (dldir, str(i), ext))
                i += 1
    if info['logos']:    
        name, ext = os.path.splitext(info['logos'][0])            
        download(info['logos'][0], '%s/clearlogo%s' % (destdir, ext))
        if len(info['logos']) > 1:    
            i = 1
            dldir = '%s/clearlogos' % destdir
            if not os.path.exists(dldir):
                os.makedirs(dldir)
            for each in info['logos']:
                name, ext = os.path.splitext(each)            
                download(each, '%s/clearlogo%s%s'  % (dldir, str(i), ext))
                i += 1
    if info['hdlogos']:    
        name, ext = os.path.splitext(info['hdlogos'][0])            
        download(info['hdlogos'][0], '%s/hdlogo%s' % (destdir, ext))
        if len(info['hdlogos']) > 1:    
            i = 1
            dldir = '%s/hdlogos' % destdir
            if not os.path.exists(dldir):
                os.makedirs(dldir)
            for each in info['hdlogos']:
                name, ext = os.path.splitext(each)            
                download(each, '%s/hdlogo%s%s' % (dldir, str(i), ext))
                #print each
                i += 1
    if info['posters']:    
        name, ext = os.path.splitext(info['posters'][0])            
        download(info['posters'][0], '%s/folder%s' (destdir, ext))
        if len(info['posters']) > 1:    
            i = 1
            dldir = '%s/posters' % destdir
            if not os.path.exists(dldir):
                os.makedirs(dldir)
            for each in info['posters']:
                name, ext = os.path.splitext(each)            
                download(each, '%s/poster%s%s' % (dldir, str(i), ext))
                #print each
                i += 1
    if info['fanart']:    
        download(info['fanart'][0], '%s/fanart.jpg' % destdir)
        if len(info['fanart']) > 1:    
            i = 1
            dldir = '%s/extrafanart' % destdir
            if not os.path.exists(dldir):
                os.makedirs(dldir)
            for each in info['fanart']:
                download(each, '%s/fanart%s.jpg' % (dldir, str(i)))
                #print each
                i += 1
    if info['thumbs']:    
        name, ext = os.path.splitext(info['thumbs'][0])            
        download(info['thumbs'][0], '%s/thumb%s' % (destdir, ext))
        if len(info['thumbs']) > 1:    
            i = 1
            dldir = '%s/extrathumbs' % destdir
            if not os.path.exists(dldir):
                os.makedirs(dldir)
            for each in info['thumbs']:
                name, ext = os.path.splitext(each)            
                download(each, '%s/thumb%s%s' % (dldir, str(i), ext))
                #print each
                i += 1
    return ''

def mergeart(info, fa):
    #print info, fa
    info['discs'].extend(fa['discs'])
    info['arts'].extend(fa['arts'])
    info['banners'].extend(fa['banners'])
    info['logos'].extend(fa['logos'])
    info['hdlogos'].extend(fa['hdlogos'])
    info['posters'].extend(fa['posters'])
    info['fanart'].extend(fa['fanart'])
    info['thumbs'].extend(fa['thumbs'])
    return info

def download(url, dest):
    try:
        urllib.urlretrieve (url, dest)
    except Exception:
        #import traceback
        #logger.error('urllib exception: %s' % traceback.format_exc())
        #print 'IOError:', url
        return 

def streaminfo(file):
    try:
        info = enzyme.parse(file)
    except:
        #print 'Error Detecting Streams: ', file
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
    #For future to check age of file in seconds
    #st=os.stat(Filename) 
    #Age=(time.time()-st.st_mtime)
    moviedir = pytunes.settings.get('movie_in', '')
    destdir = pytunes.settings.get('movie_out', '')
    total = 0
    hits = 0 
    moviepath = ''
    matched = []  
    unmatched = []
    exts = ['.avi', '.mp4', '.mkv', '.flv', '.mpeg', '.riff']
    if moviedir and destdir:  
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
    else:
        return
    paths = glob.glob('%s*' % moviedir)
    #print 'paths', paths
    for path in paths:
        match = 0
        matches = {}
        if not os.path.isfile(path):
              continue
        fileName, fileExtension = os.path.splitext(path)
        if not fileExtension in exts:
            continue
        moviepath = path    
        file = os.path.basename(path)
        #print file
        guess = guessit.guess_movie_info(file, info = ['filename'])
        #print guess
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
        #print search
        total += 1
        for s in search['results']:
            if  'year' in guess:
                if str(guess['year']) in s['release_date']:
                    match += 1
                    matches[match] = [s['title'], s['id'], s['release_date'], mimetype, container, screenSize, videoCodec, format]
                else:
                    if len(search['results']) == 1:
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

        if not matches and not search['results']:
            #print 'not matches and not search results check name'
            #print path
            unmatched.append(guess['title'])
            if not os.path.exists('%sfailed' % moviedir):
                os.makedirs('%sfailed' % moviedir)
            movie = os.path.basename(path)
            # for windows
            #import ntpath
            #ntpath.basename("a/b/c")            
            if os.path.exists(path):        
                shutil.move(path, '%sfailed%s' % (moviedir, movie))
        if not matches and search['results']:
            #need to add another layer of sophistication here!
            #right now it's just a trap to log failed matches when there were search results
            #print 'not matches and search results'
            #print path
            unmatched.append(guess['title'])
            if not os.path.exists('%sfailed' % moviedir):
                os.makedirs('%sfailed' % moviedir)
            movie = os.path.basename(path)
            # for windows
            #import ntpath
            #ntpath.basename("a/b/c")            
            if os.path.exists(path):        
                shutil.move(path, '%sfailed%s' % (moviedir, movie))
        if len(matches) == 1:
            #print 'len matches 1'
            if matches[1][2]:
                dt = datetime.strptime(matches[1][2], '%Y-%m-%d')
                year = dt.year
            else:
                year = ''
            matched.append({'title':matches[1][0], 'tmdbid':matches[1][1], 'path':moviepath, 'year':year, 'mimetype':matches[1][3], 'container':matches[1][4], 'screenSize':matches[1][5], 'videoCodec':matches[1][6], 'format':matches[1][7]})
            hits += 1
        if len(matches) > 1:
            #print 'len matches >1'
            testguess = stripall(guess['title'])
            for each in matches:
                testeach = stripall(matches[each][0])
                if testeach == testguess:
                    if matches[1][2]:
                        dt = datetime.strptime(matches[each][2], '%Y-%m-%d')
                        year = dt.year
                    else:
                        year = ''
                    matched.append({'title':matches[each][0], 'tmdbid':matches[each][1], 'path':moviepath, 'year':year, 'mimetype':matches[each][3], 'container':matches[each][4], 'screenSize':matches[each][5], 'videoCodec':matches[each][6], 'format':matches[each][7]})
                    hits += 1
                    break
                else:
                    #print 'else unmatched'
                    unmatched.append(guess['title'])
                    if not os.path.exists('%sfailed' % moviedir):
                        os.makedirs('%sfailed' % moviedir)
                    movie = os.path.basename(path)
                    # for windows
                    #import ntpath
                    #ntpath.basename("a/b/c") 
                    if os.path.exists(path):        
                        shutil.move(path,  '%sfailed%s' % (moviedir, movie))
    for movie in matched:
        info = {}
        fa_art = {}
        stream = {}
        stream = streaminfo(movie['path'])
        filename, dirname = names(movie, stream)
        if not os.path.exists(destdir + dirname):
            os.makedirs(destdir + dirname)
        info = tmdb.MovieInfo(movie['tmdbid'])
        fa_art = fanarttv.GetArt(movie['tmdbid'], 'movie')
        if fa_art:
            info = mergeart(info, fa_art)
        procpics(destdir + dirname, info) 
        shutil.move(movie['path'], destdir + dirname + '/' + filename)

