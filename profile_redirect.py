# coding=utf-8
import Globals
from Products.Five import BrowserView
from Products.Five.traversable import Traversable
from zope.app.traversing.interfaces import ITraversable
from zope.interface import implements
from zope.component import createObject

from interfaces import *
import utils

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
                
                utils.login(self.context, user)
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
                m = 'GSProfileRedirect: Going to verify the address with '\
                  'the verification ID %s for the user %s (%s).'  % \
                  (verificationId, user.getProperty('fn', ''), user.getId())
                log.info(m)
                
                utils.login(self.context, user)
                emailAddress = user.verify_emailAddress(verificationId)
                m = 'GSProfileRedirect: Verified the address <%s> for '\
                  'the user %s (%s)' % (emailAddress, 
                    user.getProperty('fn', ''), user.getId())
                log.info(m)

                uri = '/contacts/%s/verify_address.html?email=%s' %\
                  (user.getId(), emailAddress)
            else: # Cannot find user
                uri = '/r/verify-user-not-found?id=%s' % verificationId
        else: # Verification ID not specified
            uri = '/r/verify-user-no-id'
        return self.request.RESPONSE.redirect(uri)

    def admin_verified_redirect(self):
        site_root = self.context.site_root()
        acl_users = site_root.acl_users

        if len(self.request.form['subpaths']) == 1:
            verificationId = self.request.form['subpaths'][0]
            user = acl_users.get_userByPasswordVerificationId(verificationId)
            
            if user:
                m = 'GSProfileRedirect: Going to register_password.html '\
                  'for the user %s (%s), using the verification ID '\
                  '"%s"' % (user.getProperty('fn', ''), user.getId(),
                    verificationId)
                log.info(m)
                
                utils.login(self.context, user)
                # Clean up
                user.clear_userPasswordResetVerificationIds()
                
                uri = '/contacts/%s/register_password.html' % user.getId()
            else: # Cannot find user
                uri = '/r/user-not-found?id=%s' % verificationId
        else: # Verification ID not specified
            uri = '/r/user-no-id'
        return self.request.RESPONSE.redirect(uri)

    def reject_invite(self):
        site_root = self.context.site_root()
        acl_users = site_root.acl_users

        if len(self.request.form['subpaths']) == 1:
            invitationId = self.request.form['subpaths'][0]
            user = acl_users.get_userByInvitationId(invitationId) 

            if user:
                m = 'GSProfileRedirect: Going to reject_invite.html '\
                  'for the user %s (%s), using the invitation ID '\
                  '"%s"' % (user.getProperty('fn', ''), user.getId(),
                    invitationId)
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
                    'name':   user.getProperty('fn', ''),
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

                # --=mpj17=-- Check to see if we should delete the profile
                # Detete user
                uri = '/r/rejected-invitation'

            else: # Cannot find user
                uri = '/r/user-not-found?id=%s' % invitationId
        else: # Verification ID not specified
            uri = '/r/user-no-id'
        return self.request.RESPONSE.redirect(uri)


