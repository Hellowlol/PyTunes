#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytunes
import cherrypy
import logging
from sqlobject import SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol
from cherrypy.lib.auth2 import require, member_of
from pytunes.manageusers import Manageusers

class Users:
    def __init__(self):
        self.logger = logging.getLogger('modules.users')
        Manageusers.createTable(ifNotExists=True)
        pytunes.MODULES.append({
            'name': 'Manage users',
            'id': 'users',
            'action': pytunes.WEBDIR + 'users/setusers',
            'fields': [
                {'type':'select',
                 'label':'User',
                 'name':'users_user_id',
                 'options':[
                    {'name':'New', 'value':0}
                ]},
                {'type':'text',
                 'label':'Username',
                 'name':'users_user_username'},
                {'type':'password',
                 'label':'Password',
                 'name':'users_user_password'},
                {'type':'select',
                 'label':'Role',
                 'name': 'users_user_role',
                 'options': [
                    {'name': 'user', 'value':'user'},
                    {'name':'admin', 'value': 'admin'}
                    ]}
        ]})

    @cherrypy.expose()
    @require(member_of("admin")) 
    def index(self):
        return pytunes.LOOKUP.get_template('manageusers.html').render(scriptname='manageusers')

    @cherrypy.expose()
    @require(member_of("admin")) 
    def setusers(self, users_user_id, users_user_username, users_user_password, users_user_role):
        if users_user_id == "0":
            self.logger.debug('Creating Manage users in db')
            try:
                Manageusers(username=users_user_username,
                    password=users_user_password,
                    role=users_user_role)
                return 'hack'
            except Exception, e:
                self.logger.debug('Failed to create %s %s' % (users_user_username, e))
                return
        else:
            try:
                users = Manageusers.selectBy(username=users_user_username).getOne()
                users.username = users_user_username
                users.password = users_user_password
                users.role = users_user_role
                return 'hack'
            except SQLObjectNotFound, e:
                self.logger.debug('Failed to update username on %s' % users_user_username)
                return

    @cherrypy.expose()
    @require(member_of("admin")) 
    @cherrypy.tools.json_out()
    def getuser(self, id=None):
        if id:
            """ Get user info, used by settings """
            try:
                user = Manageusers.selectBy(id=id).getOne()
                return dict((c, getattr(user, c)) for c in user.sqlmeta.columns)
            except SQLObjectNotFound:
                return

        """ Get a list of all users"""
        users = []
        for s in Manageusers.select():
            users.append({'id': s.id, 'name': s.username})
        if len(users) < 1:
            return
        return {'users': users}


    @cherrypy.expose()
    @require(member_of("admin")) 
    def delusers(self, id):
        """ Delete a user """
        self.logger.debug("Deleting user " + str(id))
        Manageusers.delete(id)
        return