# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import MultiCheckBoxWidget, SelectWidget
from zope.security.interfaces import Forbidden
import interfaces

def select_widget(field, request):
    return SelectWidget(field, field.vocabulary, request)

def multi_check_box_widget(field, request):
    return MultiCheckBoxWidget(field, field.value_type.vocabulary, request)

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
        interfaceName = config.getProperty('profileInterface', '')
        if interfaceName:
            interface = getattr(interfaces, interfaceName)
            self.form_fields = form.Fields(interface)
        self.form_fields['tz'].custom_widget = select_widget
        self.form_fields['joinable_groups'].custom_widget = \
          multi_check_box_widget
        
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
        
        loggedInUser = self.request.AUTHENTICATED_USER
        user = self.context.acl_users.getUserById(loggedInUser.getId())
        print 'Woot!'
        for i in data:
            print '%s\t%s' % (i, data[i])
        print 'Wode!'
        
        self.status = u"My God, it's full of stars!"
        assert self.status
        assert type(self.status) == unicode

    def handle_set_action_failure(self, action, data, errors):
        print action
        for i in data:
            print '%s\t%s' % (i, data[i])
        for error in errors:
            print error

