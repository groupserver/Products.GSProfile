# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
import time, md5
from zope.component import createObject
from zope.formlib import form
from Products.Five.formlib.formbase import PageForm
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.XWFCore.XWFUtils import convert_int2b62, get_support_email
from Products.GSProfile.interfaces import *

import logging
log = logging.getLogger('GSProfile')

class RequestPasswordResetForm(PageForm):
    form_fields = form.Fields(IGSRequestPasswordReset)
    label = u'Reset Password'
    pageTemplateFileName = 'browser/templates/request_password_reset.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)

    @property
    def supportEmailAddress(self):
        retval = get_support_email(self.context, self.siteInfo.id)
        assert type(retval) == str
        assert '@' in retval
        return retval

    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Reset" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Reset', failure='handle_reset_action_failure')
    def handle_reset(self, action, data):
        assert self.context
        assert self.form_fields
        assert action
        assert data
        
        if self.address_exists(data['email']):
            m = u'Password Reset: sending a reset message out to the user '\
              u'with the address <%s> on the site %s (%s)' %\
              (data['email'], self.siteInfo.name, self.siteInfo.id)
            log.info(m)
            self.reset_password(data['email'])
            self.status = u'''Check your email inbox at
              <code class="email">%s</code>, where instructions on logging 
              in and setting a new password have been sent.''' % data['email']
            assert self.status
            assert type(self.status) == unicode
        else:
            url = 'request_registration.html?form.email=%s' % data['email']
            m = u'Password Reset: Redirecting from the request password'\
              u'reset page to the request registration page (%s) '\
              u'for the address <%s> on the site %s (%s)' %\
              (url, data['email'], self.siteInfo.name, self.siteInfo.id)
            log.info(m)
            
            return self.request.RESPONSE.redirect(url)

    def handle_reset_action_failure(self, action, data, errors):
        pass

    def address_exists(self, emailAddress):
        acl_users = self.context.site_root().acl_users
        user = acl_users.get_userIdByEmail(emailAddress)
        retval = user != None
        assert type(retval) == bool
        return retval

    def reset_password(self, email):
        acl_users = self.context.site_root().acl_users
        user = acl_users.get_userByEmail(email)
        assert user!= None, 'No user with email address %s' % email
        

        # Let us hope that the verification ID *is* unique
        vNum = long(md5.new(time.asctime() + email).hexdigest(), 16)
        verificationId = str(convert_int2b62(vNum))
        user.add_password_verification(verificationId)
        
        n_dict = {}
        n_dict['verificationId'] = verificationId
        n_dict['userId'] = user.getId()
        n_dict['userFn'] = user.getProperty('fn','')
        n_dict['siteName'] = self.siteInfo.get_name()
        n_dict['siteURL'] = self.siteInfo.get_url()
        user.send_notification('reset_password', 'default', n_dict=n_dict)

