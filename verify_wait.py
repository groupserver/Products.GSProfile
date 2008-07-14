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
from zope.schema import *
from Products.XWFCore import XWFUtils
from interfaces import IGSVerifyWait
from Products.CustomUserFolder.interfaces import ICustomUser
import utils

import logging
log = logging.getLogger('GSProfile')

class VerifyWaitForm(PageForm):
    label = u'Awaiting Verification'
    pageTemplateFileName = 'browser/templates/verify_wait.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSVerifyWait)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)

        self.siteInfo = createObject('groupserver.SiteInfo', context)
        site_root = context.site_root()
        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration

    @property
    def verificationEmailAddress(self):
        retval = XWFUtils.getOption(self.context, 'userVerificationEmail')
        assert type(retval) == str
        assert '@' in retval
        return retval

    @form.action(label=u'Next', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        cf = str(data.get('came_from'))
        if cf == 'None':
          cf = ''
        uri = 'register_password.html?form.came_from=%s' % cf
        return self.request.RESPONSE.redirect(uri)
        
    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    @form.action(label=u'Send', failure='handle_set_action_failure')
    def handle_send(self, action, data):
        assert data
        assert 'email' in data.keys()
        
        newEmail = data['email']
        if utils.address_exists(self.context, newEmail):
            if newEmail in self.userEmail:
                m ='GSVerifyWait: Resending verification message to ' \
                  '<%s> for the user "%s"' % (newEmail, self.context.getId())
                log.info(m)
                
                siteObj = self.siteInfo.siteObj
                utils.send_verification_message(siteObj, self.context,
                  newEmail)
                self.status = u'''Another email address verification
                  message has been sent to
                  <code class="email">%s</code>.''' % newEmail
            else:
                m ='GSVerifyWait: Attempt to use another email address ' \
                  '<%s> by the user "%s"' % (newEmail, self.context.getId())
                log.info(m)

                self.status=u'''The address
                  <code class="email">%s</code> is already registered
                  to another user.''' % newEmail
        else: # The address does not exist
            oldEmail = self.remove_old_email()
            self.add_new_email(newEmail)
            self.status = u'''Changed your email address from
              <code class="email">%s</code> to
              <code class="email">%s</code>.''' % (newEmail, oldEmail)
        assert self.status
        assert type(self.status) == unicode        

    def remove_old_email(self):
        oldEmail = self.userEmail[0]
        log.info('GSVerifyWait: Removing <%s> from the user "%s"' % \
          (oldEmail, self.context.getId()))
        self.context.remove_emailAddressVerification(oldEmail)
        self.context.remove_emailAddress(oldEmail)

        assert oldEmail not in self.context.get_emailAddresses()
        return oldEmail
        
    def add_new_email(self, email):
        log.info('GSVerifyWait: Adding <%s> to the user "%s"' % \
          (email, self.context.getId()))
        self.context.add_emailAddress(email, is_preferred=True)
        
        siteObj = self.siteInfo.siteObj
        utils.send_verification_message(siteObj, self.context, email)
        
        assert email in self.context.get_emailAddresses()
        return email
        
    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    @property
    def userEmail(self):
        retval = self.context.get_emailAddresses()
        assert retval
        return retval

    @property
    def userName(self):
        retval = u''
        retval = XWFUtils.get_user_realnames(self.context)
        return retval

