# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.GSProfile.interfaces import *

class RequestPasswordResetForm(PageForm):
    form_fields = form.Fields(IGSRequestPasswordReset)
    label = u'Reset Password'
    pageTemplateFileName = 'browser/templates/request_password_reset.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)

    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Reset" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Reset', failure='handle_reset_action_failure ')
    def handle_reset(self, action, data):
        assert self.context
        assert self.form_fields
        if form.applyChanges(self.context, self.form_fields, data):
            # Do stuff
            self.status = u'The reset-password message has been sent.'
        else:
            self.status = u'Could not send the reset-password message, '\
              u'as the changes could not be applied to the form. Please '\
              u'contact the system administrator.'
              # Log something, so the system administrator can figure out
              #   what has gone wrong.
        assert self.status
        assert type(self.status) == unicode

    def handle_reset_action_failure(self, action, data, errors):
        pass

