# coding=utf-8
'''Implementation of the Request Registration form.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.GSProfile.interfaces import *
from Products.XWFCore import XWFUtils

class RequestRegistrationForm(PageForm):
    form_fields = form.Fields(IGSRequestRegistration)
    label = u'Register'
    pageTemplateFileName = 'browser/templates/request_register.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)

    @property
    def verificationEmailAddress(self):
        retval = XWFUtils.getOption(self.context, 'userVerificationEmail')
        assert type(retval) == str
        assert '@' in retval
        return retval

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
    @form.action(label=u'Register', 
      failure='handle_register_action_failure', 
      validator='validate')
    def handle_register(self, action, data):
        assert self.context
        assert self.form_fields
        assert action
        assert data
        
        if self.address_exists(data['email']):
            self.status = u'We should go to the Password Reset page'
        else:
            self.status = u'We should go to the Edit Profile page.'
        
        assert self.status
        assert type(self.status) == unicode

    def handle_register_action_failure(self, action, data, errors):
        pass

    def address_exists(self, emailAddress):
        acl_users = self.context.site_root().acl_users
        retval = acl_users.get_userIdByEmail(emailAddress) != None
        
        assert type(retval) == bool
        return retval

