# coding=utf-8
'''Implementation of the Request Contact form.
'''
from five.formlib.formbase import PageForm
from zope.component import createObject, adapts
from zope.interface import implements, providedBy, implementedBy,\
  directlyProvidedBy, alsoProvides
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import MultiCheckBoxWidget, SelectWidget,\
  TextAreaWidget
from zope.security.interfaces import Forbidden
from zope.app.apidoc.interface import getFieldsInOrder
from interfaceCoreProfile import IGSRequestContact
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.XWFCore.XWFUtils import get_support_email
from gs.profile.email.base.emailuser import EmailUser

class GSRequestContact(PageForm):
    label = u'Request Contact'
    pageTemplateFileName = 'browser/templates/request_contact.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSRequestContact, render_context=False)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.userInfo = IGSUserInfo(context)
        self.__loggedInUser = self.__loggedInEmailUser = None
        
    @property
    def loggedInUser(self):
        if self.__loggedInUser == None:
            self.__loggedInUser = createObject('groupserver.LoggedInUser',
                                    self.context)
        assert not(self.__loggedInUser.anonymous), \
          'Contact requested by anonymous user' 
        return self.__loggedInUser

    @property
    def loggedInEmailUser(self):
        if self.__loggedInEmailUser == None:
            self.__loggedInEmailUser = \
              EmailUser(self.context, self.loggedInUser)
        return self.__loggedInEmailUser

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
        emailUser = EmailUser(self.context, self.userInfo)
        email_addresses = emailUser.get_delivery_addresses()
        if email_addresses:
            n_dict = {
                'siteName'       : self.siteInfo.name,
                'supportEmail'   : get_support_email(self.context, self.siteInfo.id),
                'requestingName' : self.loggedInUser.name,
                'requestingEmail': self.loggedInEmailUser.get_delivery_addresses()[0],
                'siteURL'        : self.siteInfo.url,
                'requestingId'   : self.loggedInUser.id
            }
            self.userInfo.user.send_notification('request_contact', 'default', n_dict=n_dict)

