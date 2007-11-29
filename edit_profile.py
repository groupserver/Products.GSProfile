# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.GSProfile.interfaces import *

class EditProfileForm(PageForm):
    label = u'Edit Profile'
    pageTemplateFileName = 'browser/templates/edit_profile.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)

        self.form_fields = form.Fields(IGSCoreProfile)
        site_root = context.site_root()
        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        interface = config.getProperty('profileInterface', '')
        if interface:
            self.form_fields = form.Fields(eval(interface))
    
    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Edit" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Edit', failure='self.handle_set_action_failure ')
    def handle_reset(self, action, data):
        assert self.context
        assert self.form_fields
        if form.applyChanges(self.context, self.form_fields, data):
            # Do stuff
            self.status = u'The password has been set.'
        else:
            self.status = u'Could not reset the password, '\
              u'as the changes could not be applied to the form. Please '\
              u'contact the system administrator.'
              # Log something, so the system administrator can figure out
              #   what has gone wrong.
        assert self.status
        assert type(self.status) == unicode

    def handle_set_action_failure(self, action, data, errors):
        pass

