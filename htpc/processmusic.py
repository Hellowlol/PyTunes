import htpc
def process():
    print 'Process Music'
    host = htpc.settings.get('qbittorrent_host', '')
    print host

