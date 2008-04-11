# coding=utf-8
from zope.schema import *
import re
from utils import get_acl_users_for_context

EMAIL_RE = r'[a-zA-Z0-9\._%-]+@([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,4}'
check_email = re.compile(EMAIL_RE).match

BANNED_DOMAINS = ['dodgit.com', 'enterto.com', 'myspamless.com',
  'e4ward.com', 'guerrillamail.biz', 'jetable.net', 'mailinator.com',
  'mintemail.com', 'vansoftcorp.com', 'plasticinbox.com', 'pookmail.com',
  'shieldedmail.net', 'sneakemail.com', 'spamgourmet.com', 'spambox.us',
  'spaml.com', 'temporaryinbox.com', 'mx0.wwwnew.eu', 'bodhi.lawlita.com',
  'mail.htl22.at', 'zoemail.net', 'despam.it']

def disposable_address(e):
    userAddress = e.lower()
    retval = reduce(lambda a, b: a or b, 
                    [d in userAddress for d in BANNED_DOMAINS], False)
    assert type(retval) == bool
    return retval

class NotAValidEmailAddress(ValidationError):
    """Not a valid email address"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return u'The text <code>%s</code> is not a valid email address. '\
          u'Please enter a valid email address.' % repr(self.value)
    def doc(self):
        return self.__str__()

class DisposableEmailAddressNotAllowed(ValidationError):
    """Disposable Email Addresses are Not Allowed"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return u'The email address <code class="email">%s</code> is '\
          u'from a disposable email-address provider. Disposable '\
          u'email-addresses cannot be used with this system. Please enter '\
          u'a permanent email address' % self.value
    def doc(self):
        return self.__str__()

class EmailAddress(ASCIILine):
    '''An email-address entry.
    '''
    def constraint(self, value):
        if not(check_email(value)):
            raise NotAValidEmailAddress(value)
        elif disposable_address(value):
            raise DisposableEmailAddressNotAllowed(value)
        # TODO: Think about banning particular addresses. GMail would
        #   skuttle any efforts to do this properly\ldots
        return True

def address_exists(context, emailAddress):
    acl_users = get_acl_users_for_context(context)
    user = acl_users.get_userIdByEmail(emailAddress)
    retval = user != None
    
    assert type(retval) == bool
    return retval

class EmailAddressExists(ValidationError):
    """Email Address already exists on the system"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return u'The email address <code class="email">%s</code> '\
          u'already exists on this site. Please enter a new address.' %\
          self.value
    def doc(self):
        return self.__str__()

class NewEmailAddress(EmailAddress):
    def constraint(self, value):
        EmailAddress.constraint(self, value)
        if address_exists(self.context, value):
            raise EmailAddressExists(value)
        return True

