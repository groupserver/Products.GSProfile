# coding=utf-8
'''The form that allows an administrator to join someone to a group.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.schema import *

from Products.XWFCore import XWFUtils
from Products.CustomUserFolder.interfaces import IGSUserInfo
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

        siteInfo = self.siteInfo = \
          createObject('groupserver.SiteInfo', context)
        groupsInfo = self.groupsInfo = \
          createObject('groupserver.GroupsInfo', context)
        groupInfo = self.groupInfo = \
          createObject('groupserver.GroupInfo', context)
        site_root = context.site_root()

        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        
        self.interfaceName = interfaceName = '%sAdminJoinSingle' %\
          config.getProperty('profileInterface', 'IGSCoreProfile')
        assert hasattr(interfaces, interfaceName), \
            'Interface "%s" not found.' % interfaceName
        self.interface = interface = getattr(interfaces, interfaceName)
        self.form_fields = form.Fields(interface, render_context=False)

        if not(request.form.get('form.tz', None)):
            siteTz = siteInfo.get_property('tz', 'UTC')
            defaultTz = groupInfo.get_property('tz', siteTz)
            request.form['form.tz'] = defaultTz
        tz = self.form_fields['tz']
        tz.custom_widget = select_widget
        
        self.form_fields['biography'].custom_widget = wym_editor_widget
         
        stdIfaceName = config.getProperty('profileInterface',
          'IGSCoreProfile')
        assert hasattr(interfaces, stdIfaceName), \
            'Interface "%s" not found.' % stdIfaceName
        stdIface = getattr(interfaces, stdIfaceName)
        self.standardFieldIds = [f[0] for f in getFieldsInOrder(stdIface)]
        
        self.__standardFields = None
        self.__adminFields = None
        self.createdUser = None
         
    @property
    def standardFields(self):
        if self.__standardFields == None:
            self.__standardFields = []
            for w in self.widgets:
                n = w.name.split(w._prefix)[1]
                if n in self.standardFieldIds:
                    self.__standardFields.append(w)
        assert type(self.__standardFields) == list
        return self.__standardFields
        
    @property
    def adminFields(self):
        if self.__adminFields == None:
            self.__adminFields = []
            for w in self.widgets:
                n = w.name.split(w._prefix)[1]
                if n not in self.standardFieldIds:
                    self.__adminFields.append(w)
        assert type(self.__adminFields) == list
        return self.__adminFields
            
    @form.action(label=u'Add', failure='handle_add_action_failure')
    def handle_add(self, action, data):
        self.actual_handle_add(action, data)

    def actual_handle_add(self, action, data):
        acl_users = self.context.acl_users
        email = data['email']

        admin = self.request.AUTHENTICATED_USER
        assert admin
        adminInfo = IGSUserInfo(admin)
        m = u'AdminJoinEditProfileForm: Admin %s (%s) joining user with '\
          u'address <%s>' % (admin.name, admin.id, email)
        log.info(m)
        
        groupMembershipId = '%s_member' % self.groupInfo.get_id()
        if utils.address_exists(self.context, email):
            m = u'AdminJoinEditProfileForm: User with the email address '\
              u'<%s> exists. Adding to %s (%s) on %s (%s).' % \
              (email, self.groupInfo.get_name(), self.groupInfo.get_id(),
                 self.siteInfo.get_name(), self.siteInfo.get_id())
            log.info(m)

            user = acl_users.get_userByEmail(email)
            assert user, 'User for address <%s> not found' % email
            userInfo = IGSUserInfo(user)
            if groupMembershipId in user.getGroups():
                self.status=u'<li>The user with the email address '\
                  u'<code class="email">%s</code> &#8213;'\
                  u'<a href="%s" class="fn">%s</a> &#8213; is '\
                  u'already a member of '\
                  u'<a class="group" href="%s">%s</a>.</li>'%\
                  (email, userInfo.url, user.name, 
                   self.groupInfo.url, self.groupInfo.name)
            else:
                self.status=u'<li>Using the existing user with the email '\
                  u'address <code class="email">%s</code>: '\
                  u'<a href="%s" class="fn">%s</a></li>' %\
                  (email, userInfo.url, userInfo.name)
        else:
            user = self.create_user(data)
            userInfo = IGSUserInfo(user)
            self.status = u'<li>The user <a href="%s">%s</a> '\
              u'has been created, and given the email address '\
              u'<code class="email">%s</code></li>''' % \
                (userInfo.url, userInfo.name, email)

        if groupMembershipId not in user.getGroups():
            utils.join_group(user, self.groupInfo)
            self.status = u'%s<li><a href="%s" class="fn">%s</a> is now '\
              u'a member of <a class="group" href="%s">%s</a>.</li>'%\
              (self.status, userInfo.url, userInfo.name, 
               self.groupInfo.url, self.groupInfo.name)
        else:
            self.status = u'%s<li>No changes have been made.</li>' % \
              self.status
        self.status = u'<ul>%s</ul>' % self.status
        self.createdUser = user
        
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
        userInfo = IGSUserInfo(user)
        # Add profile attributes 
        schema = getattr(interfaces, self.interfaceName)
        utils.enforce_schema(user, schema)
        changed = form.applyChanges(user, self.form_fields, data)
        m = 'AdminJoinEditProfileForm: Changed the attributes ' \
          'for the user %s (%s)' % (userInfo.name, userInfo.id)
        log.info(m)
        
        # Send notification
        utils.send_add_user_notification(user, self.get_admin(), 
          self.groupInfo, data.get('message', ''))
        
        return user

    def get_admin(self):
        loggedInUser = self.request.AUTHENTICATED_USER
        assert loggedInUser
        roles = loggedInUser.getRolesInContext(self.groupInfo.groupObj)
        assert ('GroupAdmin' in roles) or ('DivisionAdmin' in roles), \
          '%s is not a group admin' % loggedInUser
        return loggedInUser

