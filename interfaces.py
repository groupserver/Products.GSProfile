# coding=utf-8
"""Interfaces for the registration and password-reset pages."""
import re, pytz
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary

from interfaceCoreProfile import IGSCoreProfile
try:
    # The site profile may not exist.
    from interfaceSiteProfile import *
except ImportError, e:
    pass

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

class VID(ASCII):
    def constraint(self, value):
        acl_users = self.context.site_root().acl_users
        assert acl_users
        
        userId = acl_users.get_userIdByVerificationId(value)
        print '"%s" ⇨ "%s"' % (value, userId) 
        retval = userId != ''
        return retval

class IGSVerifyAddress(Interface):
    """Schema used to define the user interface for the verify 
    email-address form."""
    
    vid = VID(title=u'Verification Identifier',
      description=u'The indentifier for the email address that '\
        u'is being identified',
      required=True,
      min_length=23,
      max_length=23)
      
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

class IGSEditProfileMarker(Interface):
    """Marker interface for the edit profile page.
    """

class IGSUserProfileMarker(Interface):
    """Marker interface for the user's profile page.
    """
class IGSVerifyAddressMarker(Interface):
    """Marker interface for the verify email address page.
    """

