import pytunes
import os
import subprocess as sub
import glob

file = "/home/madclicker/Downloads/Eric Clapton - Old Sock (2013) MP3VBR Beolab1700"
def process():
    print 'Process Music'
    musicdir = pytunes.settings.get('music_in', '')
    destdir = pytunes.settings.get('music_out', '')
    if not os.path.exists(musicdir):
        os.makedirs(musicdir)
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    if not (musicdir.endswith('/')):
        musicdir += '/'
    if not (destdir.endswith('/')):
        destdir += '/'
    paths = glob.glob(musicdir + '/*')
    for path in paths:
        if not os.path.isdir(path):
            continue
        print path    
        #p = sub.Popen(["beet","import" ,'-d', destdir, file], stdout=sub.PIPE, stderr=sub.PIPE)
        #output, errors = p.communicate()

