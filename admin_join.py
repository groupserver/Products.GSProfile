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
        groupMembershipId = '%s_member' % self.groupInfo.get_id()
        if utils.address_exists(self.context, email):
            m = u'AdminJoinEditProfileForm: User with the email address '\
              u'<%s> exists: %s (%s). Adding to %s (%s) on %s (%s).' % \
              (email, admin.getProperty('fn', ''), admin.getId(),
               self.groupInfo.get_name(), self.groupInfo.get_id(),
                 self.siteInfo.get_name(), self.siteInfo.get_id())
            log.info(m)

            user = acl_users.get_userByEmail(email)
            assert user, 'User for address <%s> not found' % email
            
            if groupMembershipId in user.getGroups():
                self.status=u'<li>The user with the email address '\
                  u'<code class="email">%s</code> &#8213;'\
                  u'<a href="/contacts/%s" class="fn">%s</a> &#8213; is '\
                  u'already a member of '\
                  u'<a class="group" href="%s">%s</a>.</li>'%\
                  (email, user.getId(), user.getProperty('fn', ''),
                   self.groupInfo.get_url(), self.groupInfo.get_name())
            else:
                self.status=u'<li>Using the existing user with the email '\
                  u'address <code class="email">%s</code>: '\
                  u'<a href="/contacts/%s" class="fn">%s</a></li>' %\
                  (email, user.getId(), user.getProperty('fn', ''))
        else:
            user = self.create_user(data)
            self.status = u'<li>The user <a href="/contacts/%s">%s</a> '\
              u'has been created, and given the email address '\
              u'<code class="email">%s</code></li>''' % \
                (user.getId(), user.getProperty('fn', ''), email)

        if groupMembershipId not in user.getGroups():
            utils.join_group(user, self.groupInfo)
            self.status = u'%s<li><a href="/contacts/%s" class="fn">%s</a> '\
              u'is now a member of '\
              u'<a class="group" href="%s">%s</a>.</li>'%\
              (self.status, user.getId(), user.getProperty('fn', ''),
               self.groupInfo.get_url(), self.groupInfo.get_name())
        else:
            self.status = u'%s<li>No changes have been made.</li>' % \
              self.status
        self.status = u'<ul>%s</ul>' % self.status
        
    def handle_add_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def create_user(self, data):
        email  = data['email']
        m = 'AdminJoinEditProfileForm: No user with the email '\
          'address <%s>.' % email
        log.info(m)
        
        user = utils.create_user_from_email(self.context, email)

        # Add profile attributes 
        schema = getattr(interfaces, self.interfaceName)
        utils.enforce_schema(user, schema)
        changed = form.applyChanges(user, self.form_fields, data)
        m = 'AdminJoinEditProfileForm: Changed the attributes ' \
          'for the user %s (%s)' % (user.getProperty('fn', ''), user.getId())
        log.info(m)
        
        # Send notification
        utils.send_add_user_notification(user, self.get_admin(), 
          self.groupInfo, data['message'])
        
        return user

    def get_admin(self):
        loggedInUser = self.request.AUTHENTICATED_USER
        assert loggedInUser
        roles = loggedInUser.getRolesInContext(self.groupInfo.groupObj)
        assert ('GroupAdmin' in roles) or ('DivisionAdmin' in roles), \
          '%s is not a group admin' % loggedInUser
        return loggedInUser

