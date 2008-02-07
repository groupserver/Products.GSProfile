# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject, adapts
from zope.interface import implements, providedBy, implementedBy,\
  directlyProvidedBy, alsoProvides
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import MultiCheckBoxWidget, SelectWidget,\
  TextAreaWidget
from zope.app.apidoc.interface import getFieldsInOrder
from zope.schema import *
from Products.XWFCore import XWFUtils
import interfaces
import utils
from zope.app.form.browser.widget import renderElement

import logging
log = logging.getLogger('GSEditProfile')

def select_widget(field, request):
    retval = SelectWidget(field, field.vocabulary, request)
    retval.size = 15 # Because there are a lot of items.
    return retval

class NotBrokenMultiCheckBoxWidget(MultiCheckBoxWidget):
    def renderItem(self, index, text, value, name, cssClass):
        widgetId = '%s.%s' % (name, index)
        elem = renderElement('input',
                             type="checkbox",
                             cssClass=cssClass,
                             name=name,
                             id=widgetId,
                             value=value)
        label = '<label class="checkboxLabel" for="%s">%s</label>' % \
          (widgetId, text)
        return self._joinButtonToMessageTemplate %(elem, label)


def multi_check_box_widget(field, request):
    return NotBrokenMultiCheckBoxWidget(field, 
                                        field.value_type.vocabulary, 
                                        request)
    
    
def wym_editor_widget(field, request):
    retval = TextAreaWidget(field, request)
    retval.cssClass = 'wymeditor'
    return retval

class EditProfileForm(PageForm):
    label = u'Edit Profile'
    pageTemplateFileName = 'browser/templates/edit_profile.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)

        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        site_root = context.site_root()

        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        
        interfaceName = config.getProperty('profileInterface',
                                           'IGSCoreProfile')
        assert hasattr(interfaces, interfaceName), \
            'Interface "%s" not found.' % interfaceName
        self.interface = interface = getattr(interfaces, interfaceName)
        self.form_fields = form.Fields(interface, render_context=True)

        self.form_fields['tz'].custom_widget = select_widget
        self.form_fields['biography'].custom_widget = wym_editor_widget
            
        self.enforce_schema(context, interface)
        
    def enforce_schema(self, inputData, schema):
        """
        SIDE EFFECTS
          * "inputData" is stated to provide the "schema" interface
          * "inputData" will provide all the properties defined in "schema"
        """

        typeMap = {
          Text:      'ulines',
          TextLine:  'ustring',
          ASCII:     'lines',
          ASCIILine: 'string',
          URI:       'string',
          Bool:      'bool',
          Float:     'float',
          Int:       'int',
          Datetime:  'date',
          Date:      'date',
        }
        fields = [field[0] for field in getFieldsInOrder(schema)]
        for field in fields:
            if not hasattr(inputData, field):
                default = schema.get(field).default or ''
                t = typeMap.get(type(schema.get(field)), 'ustring')
                inputData.manage_addProperty(field, default, t)
        alsoProvides(inputData, schema)

    @property
    def userName(self):
        retval = u''
        retval = XWFUtils.get_user_realnames(self.context)
        return retval

    @property
    def userId(self):
        userId = self.context.getId()
        return userId
    
    @property
    def userUrl(self):
        retval = '/contacts/%s' % self.userId
        assert type(retval) == str
        assert retval
        return retval

    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Edit" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Edit', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        self.status = self.set_data(data)
        
    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def set_data(self, data):
        assert self.context
        assert self.form_fields

        fields = [field for field in getFieldsInOrder(self.interface)
                  if not field[1].readonly]
        # --=mpj17=-- There *must* be a better way to skip the joinable
        #  groups data, and still get a list of altered fields in a sane
        #  order, but I am far too tired to figure it out
        alteredFields = [datum[0] for datum in fields
                         if ((datum[0] != 'joinable_groups') and
                           (data[datum[0]] != getattr(self.context, datum[0])))]
        changed = form.applyChanges(self.context, self.form_fields, data)
        if changed:
            fields = [self.interface.get(name).title
                      for name in alteredFields]
            f = ' and '.join([i for i in (', '.join(fields[:-1]), fields[-1])
                              if i])
            retval = u'Changed %s' % f
        else:
            retval = u"No fields changed."
            
        m = 'set_data: %s (%s)' % (retval, self.context.getId())
        log.info(m)
        
        assert retval
        assert type(retval) == unicode
        return retval

class RegisterEditProfileForm(EditProfileForm):
    label = u'Edit Profile'
    pageTemplateFileName = 'browser/templates/edit_profile_register.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):

        PageForm.__init__(self, context, request)

        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        site_root = context.site_root()
        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration

        interfaceName = config.getProperty('profileInterface',
                                           'IGSCoreProfile')
        interfaceName = '%sRegister' % interfaceName 

        assert hasattr(interfaces, interfaceName), \
            'Interface "%s" not found.' % interfaceName
        self.interface = interface = getattr(interfaces, interfaceName)

        self.form_fields = form.Fields(interface, render_context=True)

        self.form_fields['tz'].custom_widget = select_widget
        self.form_fields['biography'].custom_widget = wym_editor_widget
        self.form_fields['joinable_groups'].custom_widget = \
          multi_check_box_widget

        self.enforce_schema(context, interface)
        
    @property
    def userEmail(self):
        retval = self.context.get_emailAddresses()
        assert retval
        return retval

    @form.action(label=u'Edit', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        assert data
        
        if 'joinable_groups' in data.keys():
            # --=mpj17=-- Site member?
            groupsToJoin = data.pop('joinable_groups')
            self.join_groups(groupsToJoin)
        self.form_fields = self.form_fields.omit('joinable_groups')
        self.set_data(data)
        
        if self.user_has_verified_email():
            uri = 'register_password.html'
        else:
            email = self.context.get_emailAddresses()[0]
            uri = 'verify_wait.html?form.email=%s' % email
        return self.request.RESPONSE.redirect(uri)
        
    def user_has_verified_email(self):
        email = self.context.get_emailAddresses()[0]
        retval = self.context.emailAddress_isVerified(email)
        return retval

    def join_groups(self, groupsToJoin):
        joinableGroups = \
            self.groupsInfo.get_joinable_group_ids_for_user(self.context)
        for groupId in groupsToJoin:
            assert groupId in joinableGroups, \
              '%s not a joinable group' % groupId
            m = u'RegisterEditProfileForm: adding the user %s to the '\
                u' group %s' % (self.context.getId(), groupId)
            log.info(m)
            
            userGroup = '%s_member' % groupId
            self.context.add_groupWithNotification(userGroup)

        siteGroup = '%s_member' % self.siteInfo.get_id()
        self.context.add_groupWithNotification(siteGroup)

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
        interfaceName = 'IGSCoreProfileAdminJoin'
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

            user = acl_users.get_userIdByEmail(data['email'])
            assert user, 'User for address <%s> not found' % data['email']
            self.join_group(self, user)
        else:        
            m = 'AdminJoinEditProfileForm: No user with the email '\
              'address <%s>.' % data['email']
            log.info(m)

            user = utils.create_user_from_email(self.context, data['email'])
            
            # Add profile attributes 
            changed = form.applyChanges(user, self.form_fields, data)
            m = 'AdminJoinEditProfileForm: Changed the attributes %s ' \
              'for the user "%s"' % (chaged, user.getId())
            log.info(m)
            
            # Send notification
            self.send_add_user_notification(user)
        
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

    def send_add_user_notification(self, user):
        email = user.get_emailAddresses(self)
        
        verificationId = utils.verificationId_from_email(email)
        user.add_emailAddressVerification(verificationId, email)
        n_dict = {}
        n_dict['verificationId'] = verificationId
        n_dict['userId'] = user.getId()
        n_dict['userFn'] = user.getProperty('fn','')
        n_dict['siteName'] = self.siteInfo.get_name()
        n_dict['siteURL'] = self.siteInfo.get_url()
        user.send_notification(
          n_type='admin_create_new_user', 
          n_id='default',
          n_dict=n_dict, 
          email_only=[email])
        m = 'AdminJoinEditProfileForm: Sent a notification message '\
          'to <%s> for the user "%s"' % (email, user.getId())
        log.info(m)

