# coding=utf-8
from zope.interface import implements, providedBy
from zope.component import createObject
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import IVocabulary, \
  IVocabularyTokenized, ITitledTokenizedTerm
from zope.interface.common.mapping import IEnumerableMapping 
from zope.schema import *
import re
from utils import get_acl_users_for_context

EMAIL_RE = r'^[a-zA-Z0-9\._%-]+@([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,4}$'
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
        return u'The text "%s" is not a valid email address.' % self.value
    def doc(self):
        return self.__str__()

class DisposableEmailAddressNotAllowed(ValidationError):
    """Disposable Email Addresses are Not Allowed"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return u'The email address "%s" is from a disposable '\
          u'email-address provider; disposable '\
          u'email-addresses cannot be used with this site.' % self.value
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
        return u'The email address "%s" already exists on this site.' % \
          self.value
    def doc(self):
        return self.__str__()

class NewEmailAddress(EmailAddress):
    def constraint(self, value):
        EmailAddress.constraint(self, value)
        if address_exists(self.context, value):
            raise EmailAddressExists(value)
        return True

class EmailAddressesForLoggedInUser(object): #--=mpj17=-- make generic
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context
        self.userInfo = createObject('groupserver.LoggedInUser', context)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        
        self.__addresses = None
        
    @property
    def addresses(self):
        if self.__addresses == None:
            self.__addresses = \
              self.userInfo.user.get_verifiedEmailAddresses()
        assert type(self.__addresses) == list
        return self.__addresses
        
    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        retval = [SimpleTerm(a, a, a) 
                  for a in self.addresses]
        for term in retval:
            assert term
            assert ITitledTokenizedTerm in providedBy(term)
            #assert term.token == term.value
        return iter(retval)

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.addresses)

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = value in self.addresses
        assert type(retval) == bool
        return retval

    def getQuery(self):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return self.getTermByToken(value)
        
    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        for a in self.addresses:
            if a == token:
                retval = SimpleTerm(a, a, a) 
                assert retval
                assert ITitledTokenizedTerm in providedBy(retval)
                #assert retval.token == retval.value
                return retval
        raise LookupError, token

