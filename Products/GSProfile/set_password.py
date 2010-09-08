# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
try:
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm
    
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.XWFCore import XWFUtils
from Products.GSProfile.interfaces import *
from Products.CustomUserFolder.userinfo import GSUserInfo
from Products.GSGroupMember.utils import inform_ptn_coach_of_join

from profileaudit import *

import logging
log = logging.getLogger('GSSetPassword')

def set_password(user, password):
    assert user, 'Not logged in, user is %s' % user

    user.set_password(password)

    auditer = ProfileAuditer(user).info(SET_PASSWORD)


class SetPasswordForm(PageForm):
    form_fields = form.Fields(IGSSetPassword)
    label = u'Change Password'
    pageTemplateFileName = 'browser/templates/set_password.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.userInfo = GSUserInfo(context)
        
    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_set" set to the success handler,
    #   "handle_set_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Reset" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Change', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        assert self.context
        assert self.form_fields
        assert action
        assert data
        
        loggedInUser = createObject('groupserver.LoggedInUser',
                                    self.context)
        assert not(loggedInUser.anonymous), 'Not logged in'
        
        set_password(loggedInUser.user, data['password1'])
                
        self.status = u'Your password has been changed.'
        assert type(self.status) == unicode

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>%s</p>' % errors[0]
        else:
            self.status = u'<p>There were errors:</p>'

