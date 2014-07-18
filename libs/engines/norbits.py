#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytunes
import json
import logging
import requests
import logging

def search(q, cat):
    logger = logging.getLogger('modules.torrents')
    username = pytunes.settings.get('torrents_norbits_username', '')
    passkey = pytunes.settings.get('torrents_norbits_passkey', '')

    category = {
                    'all': '',
                    'movies': 1,
                    'music': 5,
                    'tv': 2,
                    'software': 3,
                    'games': 4,
                    'books': 6
                }
    payload = {
                'username': username,
                'passkey': passkey,
                'search': str(q),
                'category': category[cat],
                'limit': 3000
            }
    try:
        result = requests.post('https://norbits.net/api2.php?action=torrents', data=json.dumps(payload))
        return result.json()
    except Exception as e:
        logger.info('Failed to search norbits ', e)
        return ''
