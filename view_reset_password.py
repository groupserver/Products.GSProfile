# coding=utf-8
import Globals
from Products.Five import BrowserView
from zope.component import createObject

from interfaces import *

import logging
log = logging.getLogger('GSProfile')

class GSResetPasswordRedirect(BrowserView):
    '''View object for standard GroupServer User-Profile Instances'''
    def __init__(self, context, request):
        assert context
        assert request
        self.context = context
        self.request = request
        siteInfo = createObject('groupserver.SiteInfo', context)
 
        verificationId = request.get('verificationId', '')
        assert verificationId, 'Verification ID not set'
        self.verificationId = verificationId

    def login_redirect(self):
        site_root = self.context.site_root()
        acl_users = site_root.acl_users
        user = acl_users.get_userByPasswordVerificationId(self.verificationId)
        assert user

        m = 'GSPasswordResetRedirect: Going to the set password page '\
          'for the user %s (%s), using the verification ID "%s"' %\
          (user.getProperty('fn', ''), user.getId(), self.verificationId)
        log.info(m)

        site_root.cookie_authentication.credentialsChanged(user, 
          user.getId(), user.get_password())

        user.clear_userPasswordResetVerificationIds()

        url = '/contacts/%s/password.html' % user.getId()
        return self.request.RESPONSE.redirect(url)

