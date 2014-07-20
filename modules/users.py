#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytunes
import cherrypy
import logging
from sqlobject import SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol



class Manageusers(SQLObject):
    """ SQLObject class for users table """
    #id = StringCol()
    username = StringCol(default=None)
    password = StringCol(default=None)
    role = StringCol(default=None)


class Users:
    def __init__(self):
        """ Add module to list of modules on load and set required settings """
        self.logger = logging.getLogger('modules.users')

        Manageusers.createTable(ifNotExists=True)
        pytunes.MODULES.append({
            'name': 'Manage users',
            'id': 'users',
            'action': pytunes.WEBDIR + 'users/setusers',
            #'test': pytunes.WEBDIR + 'xbmc/ping',
            'fields': [
                {'type':'select',
                 'label':'User',
                 'name':'users_user_id',
                 'options':[
                    {'name':'New', 'value':0}
                ]},
                #{'type':'text',
                 #'label':'User',
                 #'name':'xbmc_server_name'},
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
                    {'name':'operator', 'value': 'operator'},
                    {'name':'admin', 'value': 'admin'}
                    ]}
        ]})

    @cherrypy.expose()
    def index(self):
        return pytunes.LOOKUP.get_template('manageusers.html').render(scriptname='manageusers')

    @cherrypy.expose()
    def setusers(self, users_user_id, users_user_username, users_user_password, users_user_role):
        if users_user_id == "0":
            self.logger.debug('Creating Manage users in db')
            try:
                Manageusers(username=users_user_username,
                    password=users_user_password,
                    role=users_user_role)
                return 'hack'#True #  should be 1
            except Exception, e:
                print e
        else:
            try:
                users = Manageusers.selectBy(id=users_user_username).getOne()
                users.username = users_user_username
                users.password = users_user_password
                users.role = users_user_role
                return 1
            except SQLObjectNotFound, e:
                print 'set user error', e
                return False # Should be 0

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def getuser(self, id=None):
        if id:
            """ Get XBMC server info """
            try:
                user = Manageusers.selectBy(id=id).getOne()
                print 'if id'
                print dict((c, getattr(user, c)) for c in user.sqlmeta.columns)
                return dict((c, getattr(user, c)) for c in user.sqlmeta.columns)
            except SQLObjectNotFound:
                return

        """ Get a list of all servers and the current server """
        users = []
        for s in Manageusers.select():
            users.append({'id': s.id, 'name': s.username})
        if len(users) < 1:
            return
        print users
        try:
            current = 'dick'
            #current = self.current.name
        except AttributeError:
            current = None
        return {'users': users}
        #return {'current': current, 'users': users}


    @cherrypy.expose()
    def delusers(self, id):
        """ Delete a user """
        self.logger.debug("Deleting user " + str(id))
        Manageusers.delete(id)
        #self.changeserver()
        return