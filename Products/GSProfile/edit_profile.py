# coding=utf-8
from base64 import b64encode
from zope.formlib import form
from Products.Five.browser.pagetemplatefile \
  import ZopeTwoPageTemplateFile
from zope.app.form.browser import MultiCheckBoxWidget, SelectWidget, \
  TextAreaWidget
from zope.schema import getFieldsInOrder
from Products.XWFCore.XWFUtils import comma_comma_and
from utils import enforce_schema
from zope.app.form.browser.widget import renderElement
from zope.component import createObject
from Products.GSProfile.profileaudit import profile_interface, ProfileAuditer, CHANGE_PROFILE
from Products.CustomUserFolder.interfaces import IGSUserInfo
from gs.content.form.form import SiteForm

import logging
log = logging.getLogger('GSEditProfile')


def select_widget(field, request):
    retval = SelectWidget(field, field.vocabulary, request)
    retval.size = 15 # Because there are a lot of items.
    return retval

class NotBrokenMultiCheckBoxWidget(MultiCheckBoxWidget):
    _joinButtonToMessageTemplate = \
      u'<span class="checkboxGroup" id="checkboxgroup-%s">%s&nbsp;%s</span>'
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
        gId = widgetId.replace('.', '-')
        return self._joinButtonToMessageTemplate % (gId, elem, label)
    
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
        gId = widgetId.replace('.', '-')
        return self._joinButtonToMessageTemplate % (gId, elem, label)


def multi_check_box_widget(field, request):
    return NotBrokenMultiCheckBoxWidget(field,
                                        field.value_type.vocabulary,
                                        request)
    
    
def wym_editor_widget(field, request):
    retval = TextAreaWidget(field, request)
    retval.cssClass = 'wymeditor'
    return retval

class EditProfileForm(SiteForm):
    label = u'Change Profile'
    pageTemplateFileName = 'browser/templates/edit_profile.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        SiteForm.__init__(self, context, request)

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
        self.status = self.set_data(data, skip=['joinable_groups'])
        
    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def set_data(self, data, skip=[]):
        assert self.context
        assert self.form_fields

        alteredFields = self.audit_and_get_changed(data, skip)
        
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

    def audit_and_get_changed(self, data, skip=[]):
        fields = [field for field in getFieldsInOrder(self.interface)
                  if not field[1].readonly]
        # --=mpj17=-- There *must* be a better way to skip the joinable
        #  groups data, and still get a list of altered fields in a sane
        #  order, but I am far too tired to figure it out
        alteredFields = []
        for field in fields:
            fieldId = field[0]
            if fieldId not in skip:
                new = data.get(fieldId, '')
                old = getattr(self.context, fieldId, '')
                if (old != new):
                    new = unicode(new).encode('utf-8')
                    old = unicode(old).encode('utf-8')
                    alteredFields.append(fieldId)
                    oldNew = '%s,%s' % (b64encode(old), b64encode(new))
                    self.auditer.info(CHANGE_PROFILE, fieldId, oldNew)
        return alteredFields

