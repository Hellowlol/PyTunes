#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import pytunes
from modules.users import Manageusers
from sqlobject import SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol

SESSION_KEY = '_cp_username'

def check_credentials(username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""
    # Adapt to your needs
    try:
        #Select  one item with in username col with username (there is only one as its unique)
        userexist = Manageusers.selectBy(username=username).getOne()
        
        if userexist and userexist.password == password: 
            return None
        else:
            return u"Incorrect username or password."
    except Exception as e:
        return u"Incorrect username or password."


def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
        username = cherrypy.session.get(SESSION_KEY)
        if username:
            cherrypy.request.login = username
            for condition in conditions:
                # A condition is just a callable that returns true or false
                if not condition():
                    raise cherrypy.HTTPRedirect("/auth/login")
        else:
            raise cherrypy.HTTPRedirect("/auth/login")
    
cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)


def require(*conditions):
    """A decorator that appends conditions to the auth.require config
    variable."""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate


# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current username as cherrypy.request.login
#
# Define those at will however suits the application.

def member_of(groupname):
    def check():
        # replace with actual check if <username> is in <groupname>
        userexist = Manageusers.selectBy(username=cherrypy.request.login).getOne()
        if userexist and userexist.role == groupname:
            return cherrypy.request.login == userexist.username and groupname == userexist.role
        #return cherrypy.request.login == 'joe' and groupname == 'admin'
    return check

def name_is(reqd_username):
    return lambda: reqd_username == cherrypy.request.login

# These might be handy

def any_of(*conditions):
    """Returns True if any of the conditions match"""
    def check():
        for c in conditions:
            if c():
                return True
        return False
    return check

# By default all conditions are required, but this might still be
# needed if you want to use it inside of an any_of(...) condition
def all_of(*conditions):
    """Returns True if all of the conditions match"""
    def check():
        for c in conditions:
            if not c():
                return False
        return True
    return check


# Controller to provide login and logout actions
class AuthController(object):

    def on_login(self, username):
        print """Called on successful login"""
    
    def on_logout(self, username):
        print """Called on logout"""
        raise cherrypy.HTTPRedirect("/auth/login")
    
    def get_loginform(self, username, msg="Enter login information", from_page="/"):
        return pytunes.LOOKUP.get_template('loginform.html').render(scriptname='formlogin', from_page=from_page, msg=msg)

    @cherrypy.expose()
    def login(self, username=None, password=None, from_page="/"):
        if username is None or password is None:
            return self.get_loginform("", from_page=from_page)
        
        error_msg = check_credentials(username, password)
        if error_msg:
            return self.get_loginform(username, error_msg, from_page)
        else:
            cherrypy.session.regenerate()
            cherrypy.session[SESSION_KEY] = cherrypy.request.login = username
            self.on_login(username)
            raise cherrypy.HTTPRedirect(from_page or "/")