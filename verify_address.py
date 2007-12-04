# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.GSProfile.interfaces import *

class VerifyAddressForm(PageForm):
    form_fields = form.Fields(IGSVerifyAddress)
    label = u'Verify Email Address'
    pageTemplateFileName = 'browser/templates/verify_address.pt'
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
    @form.action(label=u'Verify', failure='handle_verify_action_failure')
    def handle_verify(self, action, data):
        assert self.context
        assert self.form_fields
        assert action
        assert data
        
        user = self.context.acl_users.get_userByVerificationId(data['vid'])
        # Log in
        emailAddress = user.verify_emailAddress(data['vid'])
        
        self.status = u'''The email address
        <code class="email">%(emailAddress)s</code>
        has been verified.
        You can now send messages from
        <code class="email">%(emailAddress)s</code> to your groups, and
        messages from your groups can be sent to 
        <code class="email">%(emailAddress)s</code>.''' % \
        {'emailAddress': emailAddress}
        assert self.status
        assert type(self.status) == unicode

    def handle_verify_action_failure(self, action, data, errors):
        pass

