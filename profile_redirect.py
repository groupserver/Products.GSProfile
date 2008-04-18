# coding=utf-8
import Globals
from Products.Five import BrowserView
from Products.Five.traversable import Traversable
from zope.app.traversing.interfaces import ITraversable
from zope.interface import implements
from zope.component import createObject
from Products.CustomUserFolder.interfaces import IGSUserInfo

from Products.GSRedirect.view import GSRedirectBase

from interfaces import *
import utils

import logging
log = logging.getLogger('GSProfile')

class GSRedirectLogin(GSRedirectBase):
    def __call__(self):
        site_root = self.context.site_root()
        acl_users = site_root.acl_users

        if len(self.traverse_subpath) == 1:
            verificationId = self.traverse_subpath[0]
            user = acl_users.get_userByPasswordVerificationId(verificationId)
            
            if user:
                userInfo = IGSUserInfo(user)
                m = 'GSProfileRedirect: Going to the set password '\
                  'page for the user %s (%s), using the verification ID '\
                  '"%s"' % (userInfo.name, userInfo.id, verificationId)
                log.info(m)
                
                utils.login(self.context, user)
                # Clean up
                user.clear_userPasswordResetVerificationIds()
                
                uri = '%s/password.html' % userInfo.url
            else: # Cannot find user
                uri = '/user-not-found?id=%s' % verificationId
        else: # Verification ID not specified
            uri = '/user-no-id'
        return self.request.RESPONSE.redirect(uri)


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
                  'the verification ID %s for the user %s (%s).'  % \
                  (verificationId, userInfo.name, userInfo.id)
                log.info(m)
                
                utils.login(self.context, user)
                emailAddress = user.verify_emailAddress(verificationId)
                m = 'GSProfileRedirect: Verified the address <%s> for '\
                  'the user %s (%s)' % (emailAddress, 
                    user.getProperty('fn', ''), user.getId())
                log.info(m)

                uri = '%s/verify_address.html?email=%s' %\
                  (userInfo.url, emailAddress)
            else: # Cannot find user
                uri = '/verify-user-not-found?id=%s' % verificationId
        else: # Verification ID not specified
            uri = '/verify-user-no-id'
        return self.request.RESPONSE.redirect(uri)

class GSRedirectAdminVerified(GSRedirectBase):
    def __call__(self):
        site_root = self.context.site_root()
        acl_users = site_root.acl_users

        if len(self.traverse_subpath) == 1:
            verificationId = self.traverse_subpath[0]
            user = acl_users.get_userByPasswordVerificationId(verificationId)
            
            if user:
                userInfo = IGSUserInfo(user)
                m = 'GSProfileRedirect: Going to register_password.html '\
                  'for the user %s (%s), using the verification ID '\
                  '"%s"' % (userInfo.name, user.id, verificationId)
                log.info(m)
                
                utils.login(self.context, user)
                
                uri = '%s/register_password.html' % userInfo.url
            else: # Cannot find user
                uri = '/user-not-found?id=%s' % verificationId
        else: # Verification ID not specified
            uri = '/user-no-id'
        return self.request.RESPONSE.redirect(uri)

class GSRedirectRejectInvite(GSRedirectBase):
    def __call__(self):
        """Reject an invitation to join a group
        """
        site_root = self.context.site_root()
        acl_users = site_root.acl_users

        if len(self.traverse_subpath) == 1:
            invitationId = self.traverse_subpath[0]
            user = acl_users.get_userByInvitationId(invitationId) 
            
            uri = ''
            if user:
                userInfo = IGSUserInfo(user)
                m = 'GSProfileRedirect: Going to reject the invitation '\
                  'for the user %s (%s), using the invitation ID '\
                  '"%s"' % (userInfo.name, userInfo.id, invitationId)
                log.info(m)
                
                utils.login(self.context, user)
                # Clean up
                #user.clear_userPasswordResetVerificationIds()
                  
                # Get Data
                invitation = user.get_invitation(invitationId)
                
                groups = getattr(site_root.Content, invitation['site_id']).groups
                grp = getattr(groups, invitation['group_id'])
                groupInfo = createObject('groupserver.GroupInfo', grp)
                siteInfo = createObject('groupserver.SiteInfo', self.context)
                
                admin = acl_users.getUser(invitation['inviting_user_id'])
                adrs = admin.get_preferredEmailAddresses()
                adminAddr = ', '.join(['<%s>' % a for a in adrs])
                
                n_dict = {
                  'admin': {
                    'id':     admin.getId(),
                    'name':   admin.getProperty('fn', ''),
                    'email':  adminAddr,
                  },
                  'user': {
                    'name':   userInfo.name,
                    'email':  user.get_emailAddresses()[0],
                  },
                  'group': {
                      'id':   groupInfo.get_id(),
                      'name': groupInfo.get_name(),
                      'url':  groupInfo.get_url(),
                  },
                  'siteName': siteInfo.get_name(),
                  'siteURL':  siteInfo.get_url(),
                }
                admin.send_notification(
                  n_type='admin_create_new_user_rejected', 
                  n_id='default',
                  n_dict=n_dict)

                if (len(user.getGroups()) <= 2):
                    m = u'reject_invite: Deleting user "%s"' % user.getId()
                    log.info(m)
                    acl_users.userFolderDelUsers([user.getId()])
                    uri = '/rejected-invitation-delete'
                else:
                    uri = '/rejected-invitation'
            else: # Cannot find user
                uri = '/user-not-found?id=%s' % invitationId
        else: # Verification ID not specified
            uri = '/user-no-id'
        assert uri
        return self.request.RESPONSE.redirect(uri)

class GSRedirectAcceptInvite(GSRedirectBase):
    def __call__(self):
        """Accept an invitation to join a group
        """
        site_root = self.context.site_root()
        acl_users = site_root.acl_users

        if len(self.traverse_subpath) == 1:
            invitationId = self.traverse_subpath[0]
            user = acl_users.get_userByInvitationId(invitationId) 
            if user:
                userInfo = IGSUserInfo(user)
                utils.login(self.context, user)
                
                uri = '%s/join_password.html?form.invitationId=%s' % \
                  (userInfo.url, invitationId)
            else: # Cannot find user
                uri = '/user-not-found?id=%s' % invitationId
        else: # Verification ID not specified
            uri = '/user-no-id'
        assert uri
        return self.request.RESPONSE.redirect(uri)

