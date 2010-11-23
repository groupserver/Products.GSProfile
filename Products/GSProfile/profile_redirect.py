# coding=utf-8
from zope.component import createObject
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSRedirect.view import GSRedirectBase
from interfaces import *
import utils
import logging
log = logging.getLogger('GSProfile')

class GSRedirectVerify(GSRedirectBase):
    def __call__(self):
        site_root = self.context.site_root()
        acl_users = site_root.acl_users

        if len(self.traverse_subpath) == 1:
            verificationId = self.traverse_subpath[0]
            user = acl_users.get_userByEmailVerificationId(verificationId)
            
            if user:
                userInfo = IGSUserInfo(user)
                m = 'GSProfileRedirect: Going to verify the address with '\
                  'the verification ID %s for the user %s (%s).' % \
                  (verificationId, userInfo.name, userInfo.id)
                log.info(m)
                
                utils.login(self.context, user)
                emailAddress = user.verify_emailAddress(verificationId)
                m = 'GSProfileRedirect: Verified the address <%s> for '\
                  'the user %s (%s)' % (emailAddress,
                    user.getProperty('fn', ''), user.getId())
                log.info(m)

                uri = '%s/verify_address.html?email=%s' % \
                  (userInfo.url, emailAddress)
            else: # Cannot find user
                uri = '/verify-user-not-found?id=%s' % verificationId
        else: # Verification ID not specified
            uri = '/verify-user-no-id'
        return self.request.RESPONSE.redirect(uri)

