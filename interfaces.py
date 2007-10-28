"""Interfaces for the registration and password-reset pages."""
import re, pytz
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary

class IGSSetPassword(Interface):
    """Schema for setting the user's password. The password is entered
      twice by the user, to confirm that it is correct."""
      
    password1 = Password(title=u'Password',
        description=u'Enter your password.',
        required=True,
        min_length=4)
        
    password2 = Password(title=u'Confirm Password',
        description=u'Confirm your password',
        required=True,
        min_length=4)

    @invariant
    def passwordsMatch(passwords):
        if passwords.password1 != passwords.password2:
            raise Invalid('Passwords do not match')


EMAIL_RE = r'[a-zA-Z0-9\._%-]+@([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,4}'
check_email = re.compile(EMAIL_RE).match

class IGSEmailAddressEntry(Interface):
    email = ASCIILine(title=u'Email Address',
        description=u'Your email address.',
        required=True,
        constraint=check_email)

class IGSRequestPasswordReset(IGSEmailAddressEntry):
    """Schema used to request that the user's password is reset.
    """

class IGSRequestRegistration(IGSEmailAddressEntry):
    """Schema use to define the user-interface that start the whole
    registration process"""
    
class IGSResendVerification(IGSEmailAddressEntry):
    """Schema use to define the user-interface that the user uses to
    resend his or her verification email, while in the middle of 
    registration."""
    
def display_name_not_nul(text):
    retval = text.strip() != u''
    assert type(retval) == bool
    return retval

class IGSCoreProfile(Interface):
    """Schema use to defile the core profile of a GroupServer user."""
    
    displayName = TextLine(title=u'Display Name',
      description=u'The name that you want other to see',
      required=True,
      min_length=1,
      constraint=display_name_not_nul)
      
    nickname = DottedName(title=u'Nickname',
      description=u'The name you wish to give your profile. It should be '
        u'a short name, that contains just letters or numbers. If you do '
        u'not set a nickname, one will be created from your display name.',
      required=False,
      min_length=1)

    timezone = Choice(title=u'Timezone',
      description=u'The timezone you wish to use',
      required=False,
      default=u'UTC',
      vocabulary=SimpleVocabulary.fromValues(pytz.common_timezones))
    
    biography = Text(title=u'Biography',
      description=u'A desciption of you.',
      required=False)

# Marker interfaces

class IGSRequestPasswordResetMarker(Interface):
    """Marker interface for the request password reset page.
    """

class IGSRequestRegistrationMarker(Interface):
    """Marker interface for the request registration page.
    """

class IGSSetPasswordMarker(Interface):
    """Marker interface for the set password page.
    """

