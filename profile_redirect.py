# coding=utf-8
import Globals
from Products.Five import BrowserView
from Products.Five.traversable import Traversable
from zope.app.traversing.interfaces import ITraversable
from zope.interface import implements

from interfaces import *

import logging
log = logging.getLogger('GSProfile')

class GSProfileRedirect(BrowserView, Traversable):
    implements(ITraversable)
    
    '''View object for standard GroupServer User-Profile Instances'''
    def __init__(self, context, request):
        assert context
        assert request
        self.context = context
        self.request = request

        request.form['subpaths'] = []

    def traverse(self, name, furtherPath):
        self.request.form['subpaths'].append(name)
        
        return self

    def login_redirect(self):
        site_root = self.context.site_root()
        acl_users = site_root.acl_users

        if len(self.request.form['subpaths']) == 1:
            verificationId = self.request.form['subpaths'][0]
            user = acl_users.get_userByPasswordVerificationId(verificationId)
            
            if user:
                m = 'GSProfileRedirect: Going to the set password '\
                  'page for the user %s (%s), using the verification ID '\
                  '"%s"' % (user.getProperty('fn', ''), user.getId(),
                    verificationId)
                log.info(m)
                
                self.login(user)
                # Clean up
                user.clear_userPasswordResetVerificationIds()
                
                uri = '/contacts/%s/password.html' % user.getId()
            else: # Cannot find user
                uri = '/r/user-not-found?id=%s' % verificationId
        else: # Verification ID not specified
            uri = '/r/user-no-id'
        return self.request.RESPONSE.redirect(uri)

    def verify_redirect(self):
        site_root = self.context.site_root()
        acl_users = site_root.acl_users

        if len(self.request.form['subpaths']) == 1:
            verificationId = self.request.form['subpaths'][0]
            user = acl_users.get_userByEmailVerificationId(verificationId)
            
            if user:
                m = 'GSProfileRedirect: Going to the email verification '\
                  'page for the user %s (%s), using the verification ID '\
                  '"%s"' % (user.getProperty('fn', ''), user.getId(),
                    verificationId)
                log.info(m)
                
                self.login(user)

                uri = '/contacts/%s/verify_address.html' % user.getId()
            else: # Cannot find user
                uri = '/r/verify-user-not-found?id=%s' % verificationId
        else: # Verification ID not specified
            uri = '/r/verify-user-no-id'
        return self.request.RESPONSE.redirect(uri)

    def login(self, user):
        assert self.context
        assert user
        site_root = self.context.site_root()
        site_root.cookie_authentication.credentialsChanged(user,
          user.getId(), user.get_password())
        m = 'GSProfileRedirect: Logged in user "%s"' % user.getId()
        log.info(m)

