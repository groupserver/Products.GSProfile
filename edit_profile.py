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
from zope.security.interfaces import Forbidden
from zope.app.apidoc.interface import getFieldsInOrder
from Products.XWFCore import XWFUtils
import interfaces
from Products.CustomUserFolder.interfaces import ICustomUser

def select_widget(field, request):
    retval = SelectWidget(field, field.vocabulary, request)
    retval.size = 15 # Because there are a lot of items.
    return retval

def multi_check_box_widget(field, request):
    return MultiCheckBoxWidget(field, field.value_type.vocabulary, request)
    
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
        #self.form_fields['joinable_groups'].custom_widget = \
        #  multi_check_box_widget
        self.enforce_schema(context, interface)
        
    def enforce_schema(self, inputData, schema):
        """
        SIDE EFFECTS
          * "inputData" is stated to provide the "schema" interface
          * "inputData" will provide all the properties defined in "schema"
        """
        from zope.schema import *
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

    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Edit" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Edit', failure='handle_set_action_failure')
    def handle_reset(self, action, data):
        assert self.context
        assert self.form_fields

        alteredFields = [datum[0] 
                         for datum in getFieldsInOrder(self.interface)
                         if data[datum[0]] != getattr(self.context, datum[0])]
        changed = form.applyChanges(self.context, self.form_fields, data)
        if changed:
            fields = [self.interface.get(name).title
                      for name in alteredFields]
            f = ' and '.join([i for i in (', '.join(fields[:-1]), fields[-1])
                              if i])
            self.status = u'Changed %s' % f
        else:
            self.status = u"No fields changed."
        assert self.status
        assert type(self.status) == unicode

    def handle_set_action_failure(self, action, data, errors):
        print action
        for i in data:
            print '%s\t%s' % (i, data[i])
        for error in errors:
            print error

