#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytunes
from urllib2 import urlopen
from urllib import quote_plus
from json import loads

def search(q, cat):
	supported_cat = ['movie', 'all']
	if cat not in supported_cat:
		return ''

	try:
		url = 'https://yts.re/api/list.json?sort=seeds&keywords=%s&order=desc' % quote_plus(q)
		result = loads(urlopen(url).read())
		if result['MovieList']:
			return result['MovieList']
		else:
			return ''
	except Exception as e:
		print 'engines yts search error %s' % e
		return ''