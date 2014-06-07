import processmovies, processtv, processmusic, searcher

def CheckMovies():
    print 'Check Movies'
    processmovies.process()

def CheckTV():
    print 'Check TV'
    #processtv.process()

def CheckMusic():
    print 'Check Music'
    #processmusic.process()

def FindMovies():
    print 'Check Music'
    searcher.FindMovies()

def schedule():
    CheckMovies()
    searcher.FindMovies()
    #CheckTV()
    #CheckMusic()


