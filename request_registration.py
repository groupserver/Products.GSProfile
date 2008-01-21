# coding=utf-8
'''Implementation of the Request Registration form.
'''
import time, md5
from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.GSProfile.interfaces import *
from Products.XWFCore import XWFUtils
import utils
import logging
log = logging.getLogger('GSProfile')

class RequestRegistrationForm(PageForm):
    form_fields = form.Fields(IGSRequestRegistration)
    label = u'Register'
    pageTemplateFileName = 'browser/templates/request_register.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.context = context
        self.request = request
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
        assert self.form_fields
        assert action
        assert data
        
        if utils.address_exists(self.context, data['email']):
            logMsg = 'RequestRegistrationForm: Registration attempted with '\
              'existing address <%s>' % data['email']
            log.info(logMsg)
            
            url = 'request_password.html?form.email=%s' % data['email']
            m = '''A user with the email address 
              <code class="email">%s</code> already exists on 
              <span class="site">%s</span>. Either
              <ul>
                <li><strong>Register</strong> another email address,</li>
                <li><a href="%s"><strong>Reset</strong> your password,</a> 
                  or</li>
                <li><a href="/login.html"><strong>Login.</strong></a>
              </ul>''' % (data['email'], self.siteInfo.get_name(), url)
            self.status = m
            self.errors = []
        else:
            email = data['email']
            user = self.create_user_from_email(email)
            utils.login(self.context, user)
            site = self.siteInfo.siteObj
            utils.send_verification_message(site, user, email)
            
            # Go to the edit-profile page
            uri = '/contacts/%s/registration_profile.html' % user.getId()
            return self.request.RESPONSE.redirect(uri)

    def handle_register_action_failure(self, action, data, errors):
        pass

    def create_user_from_email(self, email):
        assert email
        m = 'Request Registration: Creating a new user for the '\
          'address <%s>' % email
        log.info(m)
        
        userNum = long(md5.new(time.asctime() + email).hexdigest(), 16)
        userId = str(XWFUtils.convert_int2b62(userNum))

        # Ensure that the user ID is unique. There is also has a race 
        #   condition, and the loop is non-deterministic.
        acl_users = self.context.site_root().acl_users
        while (acl_users.getUserById(userId)):
            userNum = long(md5.new(time.asctime() + email).hexdigest(), 16)
            userId = str(XWFUtils.convert_int2b62(userNum))
            
        displayName = email.split('@')[0]
        
        user = acl_users.simple_register_user(email, userId, displayName)
        assert user
        m = 'Request Registration: Created a new user "%s"' % user.getId()
        log.info(m)
        return user

