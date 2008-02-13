# coding=utf-8
import Globals
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import createObject
from zope.interface import implements
from zope.interface.interface import InterfaceClass
from zope.component.interfaces import IFactory
import Products.GSContent.interfaces
from Products.XWFCore import XWFUtils
from Products.XWFCore.odict import ODict
import zope.app.apidoc.interface # 

from interfaces import *

class GSEmailSettings(BrowserView):
    '''View object for standard GroupServer User-Profile Instances'''
    def __init__(self, context, request):
        assert context
        assert request
        self.context = context
        self.request = request
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        
        self.__user = self.__get_user()
        self.__addressData = []
        self.__preferredAddresses = []

    def __get_user(self):
        assert self.context
        
        userId = self.context.getId()
        site_root = self.context.site_root()
        assert site_root
        assert hasattr(site_root, 'acl_users'), 'acl_users not found'
        acl_users = site_root.acl_users
        
        user = acl_users.getUserById(userId)
        assert user
        return user
        
    @property
    def userName(self):
        retval = u''
        retval = XWFUtils.get_user_realnames(self.__user)

        return retval
        
    def emailVisibility(self):
        config = self.context.GlobalConfiguration
        retval = config.getProperty('showEmailAddressTo', 'nobody')
        retval = retval.lower()
        assert type(retval) == str
        assert retval
        assert retval in ('nobody', 'request', 'everybody')
        return retval

    def groupMembership(self):
        u = self.__get_user()
        au = self.request.AUTHENTICATED_USER
        authUser = None
        if (au.getId() != None):
            authUser = self.context.site_root().acl_users.getUser(au.getId())
        groups = self.groupsInfo.get_member_groups_for_user(u, authUser)
        retval = [createObject('groupserver.GroupInfo', g) for g in groups]
        assert type(retval) == list
        return retval

    @property
    def userAddresses(self):
        if self.__addressData == []:
            addr = self.__user.get_emailAddresses()
            pref = self.preferredAddresses
            veri = self.__user.get_verifiedEmailAddresses()
            self.__addressData = [Address(a, pref, veri) for a in addr]
        retval = self.__addressData

        assert type(retval) == list
        return retval

    @property
    def preferredAddresses(self):
        if not self.__preferredAddresses:
            self.__preferredAddresses = self.__user.get_preferredEmailAddresses()
        retval = self.__preferredAddresses
        assert type(retval) == list
        assert len(retval) > 0
        return retval
        
    @property
    def multipleDefault(self):
        retval = len(self.preferredAddresses) > 1
        assert type(retval) == bool
        return retval

    @property
    def groupEmailSettings(self):
        folders = self.groupsInfo.get_member_groups_for_user(self.__user, self.__user)
        grps = [createObject('groupserver.GroupInfo', g) for g in folders]
        retval = [GroupEmailSetting(g, self.__user) for g in grps]
        assert type(retval) == list
        return retval

    @property
    def supportEmail(self):
        assert type(retval) == str
        retval = ''
        return retval

    def process_form(self):
        '''Process the forms in the page.
        
        This method uses the "submitted" pattern that is used for the
        XForms impementation on GroupServer. 
          * The method is called whenever the page is loaded by
            tal:define="result view/process_form".
          * The submitted form is checked for the hidden "submitted" field.
            This field is only returned if the user submitted the form,
            not when the page is loaded for the first time.
            - If the field is present, then the form is processed.
            - If the field is absent, then the method returns.
        
        RETURNS
            A "result" dictionary, that at-least contains the form that
            was submitted
        '''
        form = self.context.REQUEST.form
        result = {}
        result['form'] = form

        if form.has_key('submitted'):
            buttons = [k for k in form.keys() if '-button' in k]
            assert len(buttons) == 1, 'User pressed multiple buttons!'
            button = buttons[0]
            
            addressId = button.split('-')[0]
            address = [a for a in self.userAddresses 
                       if a.addressId == addressId][0]
            print address
            
            actionId = '%s-action' % addressId
            print form[actionId]
            
            result['error'] = False
            result['message'] = u'stuff'
            assert result.has_key('error')
            assert type(result['error']) == bool
            assert result.has_key('message')
            assert type(result['message']) == unicode
        return result
        
class Address(object):
    """Information about a user's email address
    
    ATTRIBUTES
      address:   The email address, as a string
      addressId: An identifier for the address. It is unique across all the
                 user's addresses.
      default:   True if the address is a default (alias preferred) address
                 for the user.
      verified:  True if the address has been verified as being controlled
                 by the user.
    """
    def __init__(self, emailAddress, defaultAddresses=[], 
                 verifiedAddresses=[]):
        assert type(emailAddress) == str
        assert type(defaultAddresses) == list
        assert type(verifiedAddresses) == list

        self.address = emailAddress
        addressId = emailAddress.replace('@','at')
        self.addressId = addressId
        self.default = emailAddress in defaultAddresses
        self.verified = emailAddress in verifiedAddresses

        assert type(self.address) == str
        assert type(self.addressId) == str
        assert type(self.default) == bool
        assert type(self.verified) == bool

    def __str__(self):
        defl = (self.default and 'default') or 'not default'
        veri = (self.verified and 'verified') or 'not verified'
        retval = u'Email Address <%s>: %s, %s' % (self.address, defl, veri)
        assert type(retval) == unicode
        return retval

class GroupEmailSetting(object):
    """Information about a user's group email settings.
    
    ATTRIBUTES
      group:      Information about the group.
      setting:    The delivery setting for the user, as an integer.
                    0. No email delivery (Web only)
                    1. One email per post to the default address.
                    2. One email per post to a specific address.
                    3. Daily digest of topics.
      default:    True if the messages are sent to the user's default (alias
                  preferred) email addresses.
      addresses:  The address where posts are delivered.
    """
    def __init__(self, group, user):
        assert group
        assert user
        self.group = group
        self.setting = user.get_deliverySettingsByKey(group.get_id())
        grpAddrs = user.get_specificEmailAddressesByKey(group.get_id())
        self.default = len(grpAddrs) == 0
        self.addresses = user.get_deliveryEmailAddressesByKey(group.get_id())

        assert self.group
        assert self.group == group
        assert type(self.setting) == int
        assert self.setting in range(0,4)
        assert type(self.addresses) == list

