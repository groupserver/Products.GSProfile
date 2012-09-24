# coding=utf-8
'''Implementation of the Request Contact form.
'''
from zope.cachedescriptors.property import Lazy
from zope.formlib import form
from zope.security.interfaces import Forbidden
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from interfaceCoreProfile import *
from Products.CustomUserFolder.interfaces import IGSUserInfo
from gs.profile.email.base.emailuser import EmailUser
from gs.database import getSession, getTable
from profileaudit import *
from datetime import datetime, timedelta
from gs.profile.base.page import ProfilePage
from gs.profile.notify.interfaces import IGSNotifyUser

# TODO: Move to its own product (gs.profile.requestcontact).
# TODO: Split the queries and requester off from this class.
# TODO: Turn the Request Contact email into a new-style notification.


class GSRequestContact(ProfilePage):
    label = u'Request Contact'
    pageTemplateFileName = 'browser/templates/request_contact.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSRequestContact, render_context=False)
    request24hrlimit = 5

    def __init__(self, context, request):
        super(GSRequestContact, self).__init__(context, request)

        self.__loggedInEmailUser = None
        self.auditEventTable = getTable('audit_event')
        self.now = datetime.now()

    def get_requestLimit(self):
        return self.request24hrlimit

    def count_contactRequests(self):
        """ Get a count of the contact requests by this user in the past
            24 hours."""
        if self.anonymous_viewing_page:
            raise Forbidden
        aet = self.auditEventTable
        statement = aet.select()
        au = self.request.AUTHENTICATED_USER
        authUser = self.context.site_root().acl_users.getUser(au.getId())
        authUserInfo = IGSUserInfo(authUser)
        statement.append_whereclause(aet.c.user_id == authUserInfo.id)
        td = self.now - timedelta(1)
        statement.append_whereclause(aet.c.event_date >= td)
        subsystem = 'groupserver.ProfileAudit'
        statement.append_whereclause(aet.c.subsystem == subsystem)
        statement.append_whereclause(aet.c.event_code == REQUEST_CONTACT)

        session = getSession()
        r = session.execute(statement)
        return r.rowcount

    @Lazy
    def loggedInEmailUser(self):
        retval = EmailUser(self.context, self.loggedInUserInfo)
        return retval

    @Lazy
    def anonymous_viewing_page(self):
        assert self.request
        assert self.context

        roles = self.request.AUTHENTICATED_USER.getRolesInContext(self.context)
        retval = 'Authenticated' not in roles

        assert type(retval) == bool
        return retval

    @form.action(label=u'Request Contact', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        if self.count_contactRequests() > self.request24hrlimit:
            self.status = u'The request for contact has not been sent. You '\
                u'have exceeded your daily limit of contact requests'
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
        email_addresses = \
            self.userInfo.user.get_defaultDeliveryEmailAddresses()
        if email_addresses:
            deliveryAddress = authUser.get_defaultDeliveryEmailAddresses()[0]
            n_dict = {
                'siteName': self.siteInfo.name,
                'supportEmail': self.siteInfo.get_support_email(),
                'requestingName': authUserInfo.name,
                'requestingEmail': deliveryAddress,
                'siteURL': self.siteInfo.url,
                'requestingId': authUserInfo.id,
                'message': message
            }
            self.auditer.info(REQUEST_CONTACT, n_dict['requestingId'],
                                str(n_dict))

            notify = IGSNotifyUser(self.userInfo)
            notify.send_notification('request_contact', 'default',
                                     n_dict=n_dict)
