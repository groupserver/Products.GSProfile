# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
from base64 import b64encode
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
from Products.XWFCore.XWFUtils import comma_comma_and
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSGroupMember.groupmembership import join_group
from Products.GSGroupMember.utils import inform_ptn_coach_of_join
from utils import profile_interface, enforce_schema
from zope.app.form.browser.widget import renderElement

import logging
log = logging.getLogger('GSEditProfile')
from profileaudit import *

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
        return self._joinButtonToMessageTemplate % (elem, label)
    
    def renderSelectedItem(self, index, text, value, name, cssClass):
        widgetId = '%s.%s' % (name, index)
        elem = renderElement('input',
                             type="checkbox",
                             cssClass=cssClass,
                             name=name,
                             id=widgetId,
                             value=value,
                             checked="checked")
        label = '<label class="checkboxLabel" for="%s">%s</label>' % \
          (widgetId, text)
        return self._joinButtonToMessageTemplate % (elem, label)


def multi_check_box_widget(field, request):
    return NotBrokenMultiCheckBoxWidget(field, 
                                        field.value_type.vocabulary, 
                                        request)
    
    
def wym_editor_widget(field, request):
    retval = TextAreaWidget(field, request)
    retval.cssClass = 'wymeditor'
    return retval

class EditProfileForm(PageForm):
    label = u'Change Profile'
    pageTemplateFileName = 'browser/templates/edit_profile.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)

        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.userInfo = IGSUserInfo(context)
        
        self.interface = interface = profile_interface(context)
        enforce_schema(context, interface)
        self.form_fields = form.Fields(interface, render_context=True)
        self.form_fields['tz'].custom_widget = select_widget
        self.form_fields['biography'].custom_widget = wym_editor_widget
        
    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Edit" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Change', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        self.auditer = ProfileAuditer(self.context)
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
        alteredFields = self.audit_and_get_changed(data, 
                                                   skip=['joinable_groups'])
        changed = form.applyChanges(self.context, self.form_fields, data)
        if changed:
            fields = [self.interface.get(name).title
                      for name in alteredFields]
            retval = u'Changed %s' % comma_comma_and(fields)
        else:
            retval = u"No fields changed."

        assert retval
        assert type(retval) == unicode
        return retval

    def audit_and_get_changed(self, data, skip = []):
        fields = [field for field in getFieldsInOrder(self.interface)
                  if not field[1].readonly]
        # --=mpj17=-- There *must* be a better way to skip the joinable
        #  groups data, and still get a list of altered fields in a sane
         #  order, but I am far too tired to figure it out
        alteredFields = []
        for field in fields:
            new = data.get(field[0], '')
            old = getattr(self.context, field[0], '')
            if ((field[0] not in skip) and old != new):
                alteredFields.append(field[0])
                oldNew = '%s,%s' % (b64encode(old), b64encode(new))
                self.auditer.info(CHANGE_PROFILE, field[0], oldNew)
        return alteredFields

class RegisterEditProfileForm(EditProfileForm):
    """The Change Profile page used during registration is slightly 
    different from the standard Change Profile page, as the user is able
    to join groups.
    """
    label = u'Change Profile'
    pageTemplateFileName = 'browser/templates/edit_profile_register.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):

        PageForm.__init__(self, context, request)

        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.userInfo = IGSUserInfo(self.context)
        self.interface = interface = profile_interface(context)
        enforce_schema(context, interface)

        request.form['form.tz'] = self.get_timezone() # Look, a hack!
        self.form_fields = form.Fields(interface, render_context=True)

        self.form_fields['tz'].custom_widget = select_widget
        self.form_fields['biography'].custom_widget = wym_editor_widget
        self.form_fields['joinable_groups'].custom_widget = \
          multi_check_box_widget

    def get_timezone(self):
        gTz = siteTz = self.siteInfo.get_property('tz', 'UTC')

        gIds = [i for i in self.request.form.get('form.joinable_groups',[])
                if i and i != 'None']
        # Zope Sux. For some reason, kept to itself, Zope gives me a 
        #   Resource Not Found error when I try and create a GroupInfo
        #   instance. The instance *is* created ok, but it returns a 
        #   Resource Not Found anyway. Being Zope, actually stating which
        #   resource could not be found is too hard, or too useful, so
        #   I am hacking around this. Someone should fix it after some
        #   heads have been nailed to wardrobe doors.
        groups = getattr(self.siteInfo.siteObj, 'groups')

        gTzs = []
        for gId in gIds:
            if hasattr(groups, gId):
                gTzs.append(getattr(groups, gId).getProperty('tz', siteTz))

        if gTzs:            
            tzs = {}
            for tz in gTzs:
                tzs[tz] = (tzs.get(tz, 0) + 1)
            assert len(tzs) > 0
            if len(tzs) == 1:
                gTz = tzs.keys()[0]
            else:
                gTz = siteTz

        assert gTz
        return gTz
        
    @property
    def userEmail(self):
        retval = self.context.get_emailAddresses()
        assert retval
        return retval

    @form.action(label=u'Change', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        self.auditer = ProfileAuditer(self.context)
        self.actual_handle_set(action, data)

    def actual_handle_set(self, action, data):
        if 'joinable_groups' in data.keys():
            # --=mpj17=-- Site member?
            groupsToJoin = data.pop('joinable_groups')
            self.join_groups(groupsToJoin)
        self.form_fields = self.form_fields.omit('joinable_groups')
        self.set_data(data)

        cf = str(data.get('came_from'))
        if cf == 'None':
          cf = ''
        
        if self.user_has_verified_email():
            uri = 'register_password.html?form.came_from=%s' % cf
        else:
            email = self.context.get_emailAddresses()[0]
            uri = 'verify_wait.html?form.email=%s&form.came_from=%s' %\
              (email, cf)

        return self.request.RESPONSE.redirect(uri)
        
    def user_has_verified_email(self):
        email = self.context.get_emailAddresses()[0]
        retval = self.context.emailAddress_isVerified(email)
        return retval

    def join_groups(self, groupsToJoin):
        ui = IGSUserInfo(self.context)
        joinableGroups = \
            self.groupsInfo.get_joinable_group_ids_for_user(self.context)

        for groupId in groupsToJoin:
            assert groupId in joinableGroups, \
              '%s not a joinable group' % groupId
            groupInfo = createObject('groupserver.GroupInfo', 
                                      self.groupsInfo.groupsObj,
                                      groupId)
            
            join_group(self.context, groupInfo)

            ptnCoachId = groupInfo.get_property('ptn_coach_id', '')
            if ptnCoachId:
                ptnCoachInfo = createObject('groupserver.UserFromId', 
                                            self.context, ptnCoachId)
                inform_ptn_coach_of_join(ptnCoachInfo, self.userInfo,
                                         groupInfo)

