# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.GSProfile.interfaces import *

class SetPasswordForm(PageForm):
    form_fields = form.Fields(IGSSetPassword)
    label = u'Set Password'
    pageTemplateFileName = 'browser/templates/set_password.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)

    def validate(self, action, data):
      return (form.getWidgetsData(self.widgets, self.prefix, data) +
        form.checkInvariants(self.form_fields, data))

    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Reset" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Set', failure='handle_set_action_failure', 
      validator='validate')
    def handle_set(self, action, data):
        assert self.context
        assert self.form_fields
        assert action
        assert data
        
        user = self.request.AUTHENTICATED_USER
        assert user
        user.set_password(data['password1'])
        
        self.status = u'Your password has been changed.'
        assert type(self.status) == unicode

    def handle_set_action_failure(self, action, data, errors):
        pass

