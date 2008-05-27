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
from emailaddress import NewEmailAddress, NotAValidEmailAddress,\
  DisposableEmailAddressNotAllowed, EmailAddressExists
import utils

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
        self.__groupEmailSettings = []

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
            addr.sort()
            pref = self.preferredAddresses
            veri = self.__user.get_verifiedEmailAddresses()
            self.__addressData = [Address(a, pref, veri) for a in addr]
        retval = self.__addressData

        assert type(retval) == list
        return retval

    @property
    def preferredAddresses(self):
        if self.__preferredAddresses == []:
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
        if self.__groupEmailSettings == []:
            folders = self.groupsInfo.get_member_groups_for_user(self.__user,
                self.__user)
            grps = [createObject('groupserver.GroupInfo', g) 
                    for g in folders]
            self.__groupEmailSettings = [GroupEmailSetting(g, self.__user)
                                         for g in grps]
        retval = self.__groupEmailSettings
        assert type(retval) == list
        return retval

    @property
    def verificationEmailAddress(self):
        retval = XWFUtils.getOption(self.context, 'userVerificationEmail')
        assert type(retval) == str
        assert '@' in retval
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
            
            if button == 'newAddress-button':
                assert 'newAddress' in form.keys()
                newAddress = form['newAddress']
                error, message  = self.add_email(newAddress)
            else:
                addressId = button.split('-')[0]
                address = [a for a in self.userAddresses 
                           if a.addressId == addressId][0]
                actionId = '%s-action' % addressId
                action = form[actionId]

                actions = {
                  'remove':              self.remove_address,
                  'resend_verification': self.send_verification,
                  'make_default':        self.make_default,
                  'remove_default':      self.remove_default,
                }
                if action in actions.keys():
                    error, message = actions[action](address)
                    # Reset the address information
                    self.__addressData = []
                    self.__preferredAddresses = []
                    self.__groupEmailSettings = []
                
                else:
                    error = True
                    message = u'Action <code>%s</code> not supported' % action
            result['error'] = error
            result['message'] = message
            
            assert result.has_key('error')
            assert type(result['error']) == bool
            assert result.has_key('message')
            assert type(result['message']) == unicode
        
        assert result.has_key('form')
        assert type(result['form']) == dict
        return result

    def __addrs_to_html(self, addrs):
        assert addrs
        assert type(addrs) == list
        
        h1l = [u'<code class="email">%s</code>' % a for a in addrs]
        h1 = u', '.join(h1l[:-1])
        if len(h1l) > 1:
            retval = u' and '.join([h1, h1l[-1]])
        else:
            retval = h1l[0]
        assert retval
        assert type(retval) == unicode
        return retval

    def remove_address_from_group(self, address, setting):
        assert isinstance(address, Address)
        assert isinstance(setting, GroupEmailSetting)
        
        gId = setting.group.get_id()
        addr = address.address
        grpAddrs = self.__user.remove_deliveryEmailAddressByKey(gid, addr)
        message = u'%s\n<li>Removed <code class="email">%s</code> from '\
          u'the delivery settings for '\
          u'<a class="group" href="%s">%s</a></li>' %\
          (message, address.address, setting.group.get_url(), 
            setting.group.get_name())
            
        if ((grpAddrs == []) and (setting.setting == 2)):
            # There are no group-spcific addresses, so we are reverting to
            #   default delivery.
            defl = self.preferredAddresses
            if address.address in defl:
                defl.remove(address.address)
            deflHtml = self.__addrs_to_html(defl)
            addrPlural = ((len(defl) == 1) and u'address') or u'addresses'
            message = u'%s\n<li>Messages from '\
              u'<a class="group" href="%s">%s</a> will now be sent to '\
              'your default %s: %s.</li>' %\
              (message, setting.group.get_url(), 
                setting.group.get_name(), addrPlural, deflHtml)

        elif ((grpAddrs != []) and (setting.setting == 2)):
            # The group-specific delivery email address(es) have changed
            addrsHtml = self.__addrs_to_html(grpAddrs)
            message = u'%s\n<li>Messages from '\
              u'<a class="group" href="%s">%s</a> will now be '\
              u'sent to %s.</li>' %\
              (message, setting.group.get_url(), 
                setting.group.get_name(), addrsHtml)

        assert message
        assert type(message) == unicode
        return message
        
    def verification_message(self, email):
        emailHtml = self.__addrs_to_html([email])
        retval = u'A verification message has been sent to %s to ensure '\
          u'that you control the address. Please <strong>check your '\
          u'Inbox</strong>, as well as your Junk (or Spam) folder for '\
          u'the verification message, and follow the instructions in '\
          u'the message.' % emailHtml
          
        assert retval
        assert type(retval) == unicode
        return retval
        
    ######################################
    # Email Address Modification Methods #
    ######################################
    def remove_address(self, address):
        assert isinstance(address, Address)

        assert ((address.default and self.multipleDefault) or
          (not address.default)), \
          'Will not remove the only default address <%s> from %s (%s)' %\
          (address.address, self.__user.getProperty('fn', ''), \
           self.__user.getId())

        self.__user.remove_emailAddressVerification(address.address)
        message = u'<p>Removed <code class="email">%s</code> from your '\
          u'profile.</p>' % (address.address)
        groupMsg = u''
        for setting in self.groupEmailSettings:
            if address.address in setting.addresses:
                m = self.remove_address_from_group(address, setting)
                groupMsg = u'%s%s' % (groupMsg, m)
        self.__user.remove_emailAddress(address.address)
        
        message = u'%s\n<ul>\n%s\n</ul>' % (message, groupMsg)
        retval = (False, message)

        assert len(retval) == 2
        assert type(retval[0]) == bool
        assert type(retval[1]) == unicode
        return retval
        
    def send_verification(self, address):
        assert isinstance(address, Address)
        assert not address.verified, 'Address %s already verified' % \
          address.address

        utils.send_verification_message(self.context, self.__user, 
          address.address)

        message = self.verification_message(address.address)
        error = False
        
        retval = (error, message)
        assert len(retval) == 2
        assert type(retval[0]) == bool
        assert type(retval[1]) == unicode
        return retval
        
    def make_default(self, address):
        assert isinstance(address, Address)
        assert not(address.default)
        self.__user.add_defaultDeliveryEmailAddress(address.address)
        
        error = False
        htmlAddr = self.__addrs_to_html([address.address])
        message = u'<li>Added the default address %s.</li>' % htmlAddr

        newDefl = self.preferredAddresses
        newDefl.append(address.address)
        deflHtmlAddrs = self.__addrs_to_html(newDefl)
        message = u'%s\n<li>Your default email addresses are %s</li>' %\
          (message, deflHtmlAddrs)

        message = u'<ul>%s</ul>' % message
        
        retval = (error, message)
        assert type(retval[0]) == bool
        assert type(retval[1]) == unicode
        return retval
        
    def remove_default (self, address):
        assert isinstance(address, Address)
        assert self.multipleDefault, 'There is only one default address'
        assert address.default, 'Address %s is not default' % address.address
        
        self.__user.remove_defaultDeliveryEmailAddress(address.address)
        
        error = False
        htmlAddr = self.__addrs_to_html([address.address])
        message = u'<li>Removed %s from the list of default email '\
          u'addresses.</li> ' % htmlAddr

        newDefl = self.preferredAddresses
        newDefl.remove(address.address)
        addrPlural = ((len(newDefl) == 1) and u'address is') \
          or u'addresses are'
        deflHtmlAddrs = self.__addrs_to_html(newDefl)
        message = u'%s\n<li>Your default email %s %s</li>' %\
          (message, addrPlural, deflHtmlAddrs)
        message = u'<ul>%s</ul>' % message
        
        retval = (error, message)
        assert len(retval) == 2
        assert type(retval[0]) == bool
        assert type(retval[1]) == unicode
        return retval

    def add_email(self, email):
        newEmailHtml = self.__addrs_to_html([email])
        emailChecker = NewEmailAddress(title=u'Email')
        emailChecker.context = self.context # --=mpj17=-- Legit?
        try:
            emailChecker.validate(email)
        except DisposableEmailAddressNotAllowed, e:
            error = True
            message = self.error_msg(email, unicode(e))
        except NotAValidEmailAddress, e:
            error = True
            message = self.error_msg(email, unicode(e))
        except EmailAddressExists, e:
            error = True
            message = self.error_msg(email, unicode(e))
        else:
            self.__user.add_emailAddress(email=email, is_preferred=False)
            utils.send_verification_message(self.context, self.__user, email)
            error = False
            message = u'<li>The address %s has been added to your '\
              u'profile.</li>' % newEmailHtml
            message = u'<ul>%s\n<li>%s</li></ul>' % \
              (message, self.verification_message(email))
        retval = (error, message)
        assert len(retval) == 2
        assert type(retval[0]) == bool
        assert type(retval[1]) == unicode
        return retval
        
    def error_msg(self, email, msg):
        return\
          u'Did not add the email address <code class="email">%s</code>. '\
          u'%s Please enter a new email address.' % (email, msg)

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
        addressId = emailAddress.replace('@','at').replace('-', 'dash')
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

