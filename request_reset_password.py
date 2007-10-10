from Products.Five.formlib.formbase import PageForm
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.GSProfile.interfaces import *

class RequestPasswordResetForm(PageForm):
    form_fields = form.Fields(IGSRequestPasswordReset)
    label = u'Reset Password'
    pageTemplateFileName = 'browser/templates/request_password_reset.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    @form.action(u'Reset')
    def handle_reset(self, action, data):
        pass

