# coding=utf-8
'''The form that allows an administrator to join someone to a group.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.schema import *

from Products.XWFCore import XWFUtils
import interfaces
import utils
from edit_profile import *

import logging
log = logging.getLogger('GSProfile')

class AdminJoinEditProfileForm(EditProfileForm):
    label = u'Add a New Group Member'
    pageTemplateFileName = 'browser/templates/edit_profile_admin_join.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)

        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.groupInfo = createObject('groupserver.GroupInfo', context)
        site_root = context.site_root()

        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        
        # interfaceName = config.getProperty('profileInterface',
        #                                    'IGSCoreProfile')
        self.interfaceName = interfaceName = 'IGSCoreProfileAdminJoin'
        # assert hasattr(interfaces, interfaceName), \
        #     'Interface "%s" not found.' % interfaceName
        self.interface = interface = getattr(interfaces, interfaceName)
        self.form_fields = form.Fields(interface, render_context=False)

        self.form_fields['tz'].custom_widget = select_widget
        self.form_fields['biography'].custom_widget = wym_editor_widget
            
    @form.action(label=u'Add', failure='handle_add_action_failure')
    def handle_add(self, action, data):
        acl_users = self.context.acl_users
        
        if utils.address_exists(self.context, data['email']):
            m = 'AdminJoinEditProfileForm: User with the email address '\
              '<%s> exists.' % data['email']
            log.info(m)

            user = acl_users.get_userByEmail(data['email'])
            assert user, 'User for address <%s> not found' % data['email']
            self.join_group(user)
            self.status = u'''The existing user %s has been added to
              <span class="group">%s</span>''' % \
              (user.getProperty('fn', ''), self.groupInfo.get_name())
        else:        
            m = 'AdminJoinEditProfileForm: No user with the email '\
              'address <%s>.' % data['email']
            log.info(m)

            user = utils.create_user_from_email(self.context, data['email'])
            
            # Add profile attributes 
            schema = getattr(interfaces, self.interfaceName)
            self.enforce_schema(user, schema)
            changed = form.applyChanges(user, self.form_fields, data)
            m = 'AdminJoinEditProfileForm: Changed the attributes %s ' \
              'for the user "%s"' % (changed, user.getId())
            log.info(m)
            
            # Send notification
            self.send_add_user_notification(user, data)
            
            self.status = u'''The user %s has been created, and an
              invitation message has been sent to 
              <code class="email">%s</code>''' % \
                (user.getProperty('fn', ''), data['email'])
        
    def handle_add_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def join_group(self, user):
        m = u'AdminJoinEditProfileForm: adding the user %s to the '\
            u' group %s' % (user.getId(), self.groupInfo.get_id())
        log.info(m)

        userGroups = user.getGroups()
        userGroup = '%s_member' % self.groupInfo.get_id()
        assert userGroup not in userGroups, 'User %s in %s' % \
          (user.getId(), userGroup)
        user.add_groupWithNotification(userGroup)

        siteGroup = '%s_member' % self.siteInfo.get_id()
        if siteGroup not in userGroups:
            m = u'AdminJoinEditProfileForm: the user "%s" (%s) is not a '\
                u' member of the site "%s" (%s)' % \
                  (user.getId(), user.getProperty('fn', ''),
                   self.siteInfo.get_name(), self.siteInfo.get_id())
            log.info(m)
            self.context.add_groupWithNotification(siteGroup)

    def send_add_user_notification(self, user, data):
        email = user.get_emailAddresses()[0]
        
        invitationId = utils.verificationId_from_email(email)
        admin = self.get_admin()

        user.add_invitation(invitationId, admin.getId(),
          self.siteInfo.get_id(), self.groupInfo.get_id())
        user.add_emailAddressVerification(invitationId, email)
        
        n_dict = {}
        n_dict['verificationId'] = invitationId
        n_dict['userId'] = user.getId()
        n_dict['userFn'] = user.getProperty('fn','')
        n_dict['siteName'] = self.siteInfo.get_name()
        n_dict['groupName'] = self.groupInfo.get_name()
        n_dict['siteURL'] = self.siteInfo.get_url()
        n_dict['admin'] = {
          'name':    admin.getProperty('fn', ''),
          'address': admin.get_preferredEmailAddresses()[0],
          'message': data['message']}
        
        user.send_notification(
          n_type='admin_create_new_user', 
          n_id='default',
          n_dict=n_dict, 
          email_only=[email])

    def get_admin(self):
        loggedInUser = self.request.AUTHENTICATED_USER
        assert loggedInUser
        roles = loggedInUser.getRolesInContext(self.groupInfo.groupObj)
        assert ('GroupAdmin' in roles) or ('SiteAdmin' in roles), \
          '%s is not a group admin' % loggedInUser
        return loggedInUser

