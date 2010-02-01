# coding=utf-8
"""Interfaces for the registration and password-reset pages."""
import re, pytz
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary
from zope.contentprovider.interfaces import IContentProvider
from interfaceCoreProfile import *
from emailaddress import EmailAddress
try:
    # The site profile may not exist.
    from interfaceSiteProfile import *
except ImportError, e:
    pass

# Address Forms

class IGSEmailAddressEntry(Interface):
    email = EmailAddress(title=u'Email Address',
        description=u'Your email address.',
        required=True)

class IGSRequestPasswordReset(IGSEmailAddressEntry):
    """Schema used to request that the user's password is reset.
    """

# Email Address Verification

class VIDNotFound(ValidationError):
    """Email Address verification identifier not found"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'Verification identifier %s not found' % repr(self.value)
    def doc(self):
        return self.__str__()
        
class VID(ASCIILine):
    """Email Address Verification ID"""
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

class IGSFormWidgets(Interface):
    widgets = List(title=u'Widgets',
      description=u'Widgets to be displayed',
      required=True,
      unique=True)

    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '\
        u'widgets.',
      required=False,
      default=u"browser/templates/form_widgets.pt")

# Marker interfaces

class IGSRequestPasswordResetMarker(Interface):
    """Marker interface for the request password reset page.
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
class IGSUserProfiles(Interface):
    """Marker interface for the user profiles."""

class IGSViewProfileJavaScriptContentProvider(IContentProvider):
    """The content provider for the javascript"""
    
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '\
        u'javascript.',
      required=False,
      default=u"browser/templates/viewprofilejavascript.pt")

class IGSRequiredWidgetsJavaScriptContentProvider(IContentProvider):
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '\
        u'javascript.',
      required=False,
      default=u"browser/templates/requiredwidgetsjavascript.pt")

    widgets = List(title=u'Widgets',
      description=u'Widgets that are required',
      required=True,
      unique=True)

    button = ASCIILine(title=u'Button',
        description=u'The ID of the button to lock if the required '\
          u'widgets are not filled out.',
        required=True)

# Passwords

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

class IGSSetPasswordAdminJoin(IGSSetPassword):
    invitationId = ASCIILine(title=u'Invitation Identifier',
      description=u'The identifier sent to you when you were invited to '\
        u'join the group.',
      required=True)

