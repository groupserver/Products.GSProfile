# coding=utf-8
'''Implementation of the Request Contact form.
'''
try:
    from five.formlib.formbase import PageForm
except ImportError:
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
from Products.XWFCore import XWFUtils
from interfaceCoreProfile import *
from Products.CustomUserFolder.interfaces import ICustomUser, IGSUserInfo
from Products.XWFCore.XWFUtils import get_support_email

class GSRequestContact(PageForm):
    label = u'Request Contact'
    pageTemplateFileName = 'browser/templates/request_contact.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSRequestContact, render_context=False)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.userInfo = IGSUserInfo(context)

    @property
    def anonymous_viewing_page( self ):
        assert self.request
        assert self.context

        roles = self.request.AUTHENTICATED_USER.getRolesInContext(self.context)
        retval = 'Authenticated' not in roles
        
        assert type(retval) == bool
        return retval

    @form.action(label=u'Request Contact', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        assert self.context
        self.request_contact()
        self.status = u'The request for contact has been sent to %s.' \
          % self.userInfo.name
        assert self.status
        assert type(self.status) == unicode

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def request_contact(self):
        au = self.request.AUTHENTICATED_USER
        assert au, 'Contact requested by anonymous user'
        authUser = self.context.site_root().acl_users.getUser(au.getId())
        authUserInfo = IGSUserInfo(authUser)
        email_addresses = self.userInfo.user.get_defaultDeliveryEmailAddresses()
        if email_addresses:
            n_dict = {
                'siteName'       : self.siteInfo.name,
                'supportEmail'   : get_support_email(self.context, self.siteInfo.id),
                'requestingName' : authUserInfo.name,
                'requestingEmail': authUser.get_defaultDeliveryEmailAddresses()[0],
                'siteURL'        : self.siteInfo.url,
                'requestingId'   : authUserInfo.id
            }
            self.userInfo.user.send_notification('request_contact', 'default', n_dict=n_dict)

