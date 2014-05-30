import processmovies, processtv, processmusic

def CheckMovies():
    #print 'Check Movies'
    processmovies.process()

def CheckTV():
    #print 'Check TV'
    processtv.process()

def CheckMusic():
    #print 'Check Music'
    processmusic.process()

def schedule():
    CheckMovies()
    #CheckTV()
    #CheckMusic()


