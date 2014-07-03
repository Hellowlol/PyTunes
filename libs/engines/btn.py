#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jsonrpclib
import pytunes
import logging
from pytunes.staticvars import get_var as html
from json import dumps


def search(q, cat=None):
    logger = logging.getLogger('modules.torrents')
    btn = jsonrpclib.Server('http://api.btnapps.net')
    result = btn.getTorrents(pytunes.settings.get('torrents_btnapikey', ''), q, 999)
    icon = "<img alt='icon' src='../img/btn.png'/>"
    out = ''
    supported_cat = ['tv', 'all']
    if cat not in supported_cat:
        return ''

    try:
        if 'torrents' in result:
            for k,v in result['torrents'].iteritems():
                if v['Seeders'] >= pytunes.settings.get('torrents_seeds', ''):
                    link = 'https://broadcasthe.net/torrents.php?id=%s&torrentid=%s' % (v['GroupID'], v['TorrentID'])
                    name = "<a href='" + link + "' target='_blank'>" + v['ReleaseName'] + "</a>"
                    out += html('torrent_search_table') % (icon, name, sizeof(int(v['Size'])), v['Seeders'], v['Leechers'], 'BTN', v['DownloadURL'], pytunes.settings.get('default_torr_id'))
            return out
        else:
            logger.info("Couldn't find %s on BTN" % q)
            return ''

    except Exception as e:
        logger.error('Failed to find %s on BTN %s' % (q, e))
        return ''

def sizeof(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f %s" % (num, 'TB')
