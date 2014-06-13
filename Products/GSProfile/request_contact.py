# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta
from zope.cachedescriptors.property import Lazy
from zope.formlib import form
#from zope.security.interfaces import Unauthorized
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.core import to_unicode_or_bust
from gs.content.form.base import SiteForm
from gs.database import getSession, getTable
from gs.profile.email.base.emailuser import EmailUser
from gs.profile.notify.interfaces import IGSNotifyUser
from Products.CustomUserFolder.interfaces import IGSUserInfo
from .interfaceCoreProfile import IGSRequestContact
from .profileaudit import REQUEST_CONTACT, ProfileAuditer

# TODO: Move to its own product (gs.profile.requestcontact).
# TODO: Split the queries and requester off from this class.
# TODO: Turn the Request Contact email into a new-style notification.


class GSRequestContact(SiteForm):
    label = 'Request Contact'
    pageTemplateFileName = 'browser/templates/request_contact.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSRequestContact, render_context=False)
    request24hrlimit = 5

    def __init__(self, context, request):
        super(GSRequestContact, self).__init__(context, request)
        self.userInfo = IGSUserInfo(context)
        self.auditEventTable = getTable('audit_event')
        self.now = datetime.now()

    def get_requestLimit(self):
        return self.request24hrlimit

    def count_contactRequests(self):
        """ Get a count of the contact requests by this user in the past
            24 hours."""
        if self.anonymous_viewing_page:
            # FIXME: Figure out why raising Unauthorized does not work.
            # m = 'You must be logged in to request contact with someone.'
            #raise Unauthorized(m)
            uri = '/login.html?came_from=%s/request_contact.html' % \
                self.userInfo.url
            return self.request.RESPONSE.redirect(uri)

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
        retval = EmailUser(self.context, self.loggedInUser)
        return retval

    @Lazy
    def anonymous_viewing_page(self):
        assert self.request
        assert self.context

        roles = self.request.AUTHENTICATED_USER.getRolesInContext(self.context)
        retval = 'Authenticated' not in roles

        assert type(retval) == bool
        return retval

    @form.action(label='Request Contact', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        if self.count_contactRequests() > self.request24hrlimit:
            self.status = 'The request for contact has not been sent. You '\
                'have exceeded your daily limit of contact requests'
        else:
            self.auditer = ProfileAuditer(self.context)
            assert self.context

            message = to_unicode_or_bust(data.get('message', ''))
            self.request_contact(message)
            self.status = 'The request for contact has been sent to %s.' \
                % self.userInfo.name

        assert self.status

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = '<p>There is an error:</p>'
        else:
            self.status = '<p>There are errors:</p>'

    def request_contact(self, message):
        au = self.request.AUTHENTICATED_USER
        assert au, 'Contact requested by anonymous user'
        authUser = self.context.site_root().acl_users.getUser(au.getId())
        authUserInfo = IGSUserInfo(authUser)
        email_addresses = self.loggedInEmailUser.get_delivery_addresses()
        if email_addresses:
            aeu = EmailUser(self.context, authUserInfo)
            deliveryAddress = aeu.get_delivery_addresses()[0]
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
