#AUTHORS: Christophe Dumez (chris@qbittorrent.org)
from nova.helpers import retrieve_url, download_file
import json
import htpc

def download_torrent(info):
    print download_file(info, info)

def search(what, cat='all'):
    seeds = htpc.settings.get('torrents_seeds', '')
    url = 'https://kickass.to'
    name = 'kickasstorrents'
    supported_categories = {'all': '', 'movies': 'Movies', 'tv': 'TV', 'music': 'Music', 'games': 'Games', 'software': 'Applications'}
    ret = []
    i = 1
    hits = 0
    while True and i<11:
        results = []
        json_data = retrieve_url(url+'/json.php?q=%s&page=%d'%(what, i))
        try:
            json_dict = json.loads(json_data)
        except:
            i += 1
            continue
        if int(json_dict['total_results']) <= 0: return
        results = json_dict['list']
        for r in results:
            try:
                if cat != 'all' and supported_categories[cat] != r['category']: continue
                if r['seeds'] >= int(seeds):
                    res_dict = dict()
                    res_dict['name'] = r['title']
                    res_dict['size'] = str(r['size'])
                    res_dict['seeds'] = r['seeds']
                    res_dict['leech'] = r['leechs']
                    res_dict['link'] = r['torrentLink']
                    res_dict['desc_link'] = r['link']
                    res_dict['engine_url'] = url
                    ret.append(res_dict)
            except:
                pass
        i += 1
    return sorted(ret, reverse=True, key=lambda k: k['seeds'])
    
      
