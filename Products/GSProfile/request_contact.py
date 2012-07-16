# coding=utf-8
'''Implementation of the Request Contact form.
'''
try:
    from Products.Five.formlib.formbase import PageForm
except ImportError:
    from five.formlib.formbase import PageForm
    
import sqlalchemy as sa
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
from gs.profile.email.base.emailuser import EmailUser
from gs.database import getSession, getTable
from profileaudit import *
from datetime import datetime, timedelta
from gs.profile.notify.interfaces import IGSNotifyUser

class GSRequestContact(PageForm):
    label = u'Request Contact'
    pageTemplateFileName = 'browser/templates/request_contact.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSRequestContact, render_context=False)
    request24hrlimit = 5

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.userInfo = IGSUserInfo(context)
        self.__loggedInUser = self.__loggedInEmailUser = None
        self.auditEventTable = getTable('audit_event')
        self.now = datetime.now()

    def get_requestLimit(self):
        return self.request24hrlimit

    def count_contactRequests(self):
        """ Get a count of the contact requests by this user in the past
            24 hours.

        """
        aet = self.auditEventTable
        statement = aet.select()
        au = self.request.AUTHENTICATED_USER
        authUser = self.context.site_root().acl_users.getUser(au.getId())
        authUserInfo = IGSUserInfo(authUser)
        statement.append_whereclause(aet.c.user_id==authUserInfo.id)
        statement.append_whereclause(aet.c.event_date>=(self.now-timedelta(1)))
        statement.append_whereclause(aet.c.subsystem=='groupserver.ProfileAudit')
        statement.append_whereclause(aet.c.event_code==REQUEST_CONTACT)
        
        session = getSession()
        r = session.execute(statement)

        return r.rowcount

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
        if self.count_contactRequests() > self.request24hrlimit:
            self.status = u'The request for contact has not been sent. You have exceeded your daily limit of contact requests'
        else:
            self.auditer = ProfileAuditer(self.context)
            assert self.context
            
            message = data.get('message', u'')
            if not isinstance(message, unicode):
                message = unicode(message).encode('utf-8')

            self.request_contact(message)
            self.status = u'The request for contact has been sent to %s.' \
                % self.userInfo.name
         
        assert self.status
        assert type(self.status) == unicode

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def request_contact(self, message):
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
                'requestingId'   : authUserInfo.id,
                'message': message
            }
            self.auditer.info(REQUEST_CONTACT, n_dict['requestingId'], str(n_dict))

            notify = IGSNotifyUser(self.userInfo)
            notify.send_notification('request_contact', 'default',
                                     n_dict=n_dict)

