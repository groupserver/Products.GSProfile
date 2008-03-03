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
        
        self.interfaceName = interfaceName = '%sAdminJoinSingle' %\
          config.getProperty('profileInterface', 'IGSCoreProfile')
        assert hasattr(interfaces, interfaceName), \
            'Interface "%s" not found.' % interfaceName
        self.interface = interface = getattr(interfaces, interfaceName)
        self.form_fields = form.Fields(interface, render_context=False)

        self.form_fields['tz'].custom_widget = select_widget
        self.form_fields['biography'].custom_widget = wym_editor_widget
            
    @form.action(label=u'Add', failure='handle_add_action_failure')
    def handle_add(self, action, data):
        acl_users = self.context.acl_users
        email = data['email']
        admin = self.request.AUTHENTICATED_USER
        assert admin
        if utils.address_exists(self.context, email):
            m = u'AdminJoinEditProfileForm: User with the email address '\
              u'<%s> exists: %s (%s). Adding to %s (%s) on %s (%s).' % \
              (email, admin.getProperty('fn', ''), admin.getId(),
               self.groupInfo.get_name(), self.groupInfo.get_id(),
                 self.siteInfo.get_name(), self.siteInfo.get_id())
            log.info(m)

            user = acl_users.get_userByEmail(email)
            assert user, 'User for address <%s> not found' % email
            self.status = u'The existing user '\
              u'<a class="fn" href="/contacts/%s">%s</a> '\
              u'has been added to <span class="group">%s</span>.' % \
              (user.getId(), user.getProperty('fn', ''), 
                self.groupInfo.get_name())
        else:        
            m = 'AdminJoinEditProfileForm: No user with the email '\
              'address <%s>; creating user for .' % email
            log.info(m)

            user = utils.create_user_from_email(self.context, email)

            # Add profile attributes 
            schema = getattr(interfaces, self.interfaceName)
            utils.enforce_schema(user, schema)
            changed = form.applyChanges(user, self.form_fields, data)
            m = 'AdminJoinEditProfileForm: Changed the attributes ' \
              'for the user "%s"' % user.getId()
            log.info(m)
            
            # Send notification
            utils.send_add_user_notification(user, admin, 
              self.groupInfo, data['message'])

            self.status = u'''The user %s has been created, and an
              invitation message has been sent to 
              <code class="email">%s</code>''' % \
                (user.getProperty('fn', ''), email)

        utils.join_group(user, self.groupInfo)
        
    def handle_add_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def get_admin(self):
        loggedInUser = self.request.AUTHENTICATED_USER
        assert loggedInUser
        roles = loggedInUser.getRolesInContext(self.groupInfo.groupObj)
        assert ('GroupAdmin' in roles) or ('DivisionAdmin' in roles), \
          '%s is not a group admin' % loggedInUser
        return loggedInUser

