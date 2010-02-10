# coding=utf-8
'''Implementation of the Reset Password Request form.
'''
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
            self.status=u'<p>%s</p>' % errors[0]
        else:
            self.status = u'<p>There were errors:</p>'

class SetPasswordRegisterForm(SetPasswordForm):
    form_fields = form.Fields(IGSSetPasswordRegister)
    label = u'Set Password'
    pageTemplateFileName = 'browser/templates/set_password_register.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
        
    @form.action(label=u'Set', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        assert self.context
        assert self.form_fields
        assert action
        assert data

        loggedInUser = createObject('groupserver.LoggedInUser',
                                    self.context)
        assert not(loggedInUser.anonymous), 'Not logged in'
        user = loggedInUser.user
        
        set_password(user, data['password1'])
        
        # Clean up
        user.clear_userPasswordResetVerificationIds()
        uri = str(data.get('came_from'))
        if uri == 'None':
          uri = '/'
        uri = '%s?welcome=1' % uri
        return self.request.RESPONSE.redirect(uri)

class SetPasswordAdminJoinForm(SetPasswordForm):
    form_fields = form.Fields(IGSSetPasswordAdminJoin)
    label = u'Set Password'
    pageTemplateFileName = 'browser/templates/set_password_join.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)

    @form.action(label=u'Set', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        assert self.context
        assert self.form_fields
        assert action
        assert data

        loggedInUser = createObject('groupserver.LoggedInUser',
                                    self.context)
        assert not(loggedInUser.anonymous), 'Not logged in'
        
        set_password(user, data['password1'])

        site_root = self.context.site_root()
        invitation = user.get_invitation(data['invitationId'])
        groups = getattr(site_root.Content, invitation['site_id']).groups
        grp = getattr(groups, invitation['group_id'])
        groupInfo = createObject('groupserver.GroupInfo', grp)

        # Add User to the Group
        userGroup = '%s_member' % groupInfo.get_id()
        if userGroup not in user.getGroups():
            user.add_groupWithNotification(userGroup)
        assert userGroup in user.getGroups()
        user.remove_invitations()
        user.verify_emailAddress(data['invitationId'])

        ptnCoachId = groupInfo.get_property('ptn_coach_id', '')
        if ptnCoachId:
            ptnCoachInfo = createObject('groupserver.UserFromId', 
                                        self.context, ptnCoachId)
            inform_ptn_coach_of_join(ptnCoachInfo, self.userInfo, groupInfo)
        
        uri = '%s?welcome=1' % groupInfo.get_url()
        m = u'SetPasswordAdminJoinForm: redirecting user to %s' % uri
        log.info(m)
        return self.request.RESPONSE.redirect(uri)

