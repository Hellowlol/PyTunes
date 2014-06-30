#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytunes
import urllib2
import urllib
import json
import logging

def search(q=None, cat=None):
    logger = logging.getLogger('modules.torrents')
    d = {}
    d['all'] = 0
    d['music'] = 1
    d['movies'] = 3
    d['tv'] = 78
    d['books'] = 7
    d['anime'] = 5
    d['games'] = 4
    d['software'] = 6
    
    try:
        url = "http://fenopy.se/module/search/api.php?keyword=%s&sort=peer&format=json&limit=100&category=%s" % (urllib.quote_plus(q), d[cat])
        result = urllib2.urlopen(url).read()
        if 'error: no match found' in result:
            print "fucking error"
            return ''

        r = json.JSONDecoder('UTF-8').decode(result)
        return r

    except Exception as e:
        logger.error('Fenopy error while searching for %s %s' %(q, e))
        return '' 
    
    

