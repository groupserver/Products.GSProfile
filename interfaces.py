# coding=utf-8
"""Interfaces for the registration and password-reset pages."""
import re, pytz
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary
from zope.contentprovider.interfaces import IContentProvider
from interfaceCoreProfile import *
try:
    # The site profile may not exist.
    from interfaceSiteProfile import *
except ImportError, e:
    pass

class IGSSetPassword(Interface):
    """Schema for setting the user's password. The password is entered
      twice by the user, to confirm that it is correct."""
      
    password1 = Password(title=u'Password',
        description=u'Your new password. For security, your password '\
          u'should contain a mixture of letters and numbers, and '\
          u'must be over four letters long.',
        required=True,
        min_length=4)
        
    password2 = Password(title=u'Confirm Password',
        description=u'Confirm your new password by repeating it here.'\
          u'What you type in this field must match what you type in the '\
          u'Password field.',
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

class IGSVerifyWait(IGSEmailAddressEntry):
    """Schema use to define the user-interface presented while the user
    waits for verification of his or her email address."""

class VIDNotFound(ValidationError):
    """Verification identifier not found"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'Verification identifier %s not found' % repr(self.value)
    def doc(self):
        return self.__str__()
        
class VID(ASCIILine):
    def constraint(self, value):
        acl_users = self.context.site_root().acl_users
        assert acl_users
        
        userId = acl_users.get_userIdByEmailVerificationId(value)
        if userId == '':
            raise VIDNotFound(value)
        return True

class IGSVerifyAddress(Interface):
    """Schema used to define the user interface for the verify 
    email-address form."""
    
    vid = VID(title=u'Verification Identifier',
      description=u'The indentifier for the email address that '\
        u'is being identified',
      required=True,
      min_length=22,
      max_length=24)

class IGSProfileContextMenuContentProvider(IContentProvider):
    """The content provider for the context menu"""
    
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '\
        u'menu.',
      required=False,
      default=u"browser/templates/profileContextMenu.pt")
      
    pages = Dict(title=u'Pages in the Profile',
      description=u'The pages that are in the context of the profile.')

class IGSUserImage(IContentProvider):
    """User Image"""
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '\
        u'menu.',
      required=False,
      default=u"browser/templates/userImage.pt")

    user = Field(title=u'User Instance',
        description=u'An instance of the CustomUser Class',
        required=True)
        
    showImageRegardlessOfUserSetting = Bool(
      title=u'Show Image Regardles of User Setting',
      description=u"Show the user's image, regardless of the value of "
        u"the showImage property. This should be used with extreme "
        u"caution, as it can violate the user's privacy.",
      required=False,
      default=False)      

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
class IGSReigstration(Interface):
    """Marker interface for the entire registration system.
    """

