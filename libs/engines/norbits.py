#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytunes
import json
import logging
import re
import requests


class norbits:
	def __init__(self):
		self.logger = logging.getLogger('modules.torrents')
		self.username = pytunes.settings.get('torrents_norbits_username', '')
		self.passkey = pytunes.settings.get('torrents_norbits_passkey', '')
		self.urls = {
						'search': 'https://norbits.net/api2.php?action=torrents',
						'downloadurl': 'https://norbits.download.php?id=%s&passkey=%s'
						}

		self.category = {
							'all': 6,
							'movies': 1,
							'music': 5,
							'tv': 2,
							'software': 3,
							'games': 4,
							'books': 6
						} # check the categorys they are not correct.

	def search(self, q='', cat=''):
		payload = {
					'username': self.username,
					'passkey': self.passkey,
					'search': str(q),
					'category': self.category[cat],
					'limit': 3000
		}

		print 'payload is ', payload
		print 'self url is ', self.urls['search']

		try:
			result = requests.post(self.urls['search'], data=json.dumps(payload))
			return result.content
		except Exception as e:
			print 'Failed to search norbits ', e 
			self.logger.error('Failed to search for ' + q)
			return
