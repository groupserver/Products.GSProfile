# coding=utf-8
from zope.schema import ASCIILine, Bool, Dict, Field, URI, List, Text,\
    ValidationError #@UnusedImport
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Interface, invariant, Invalid #@UnusedImport
from zope.component import createObject

from interfaceCoreProfile import * #@UnusedWildImport
try:
    # The site profile may not exist.
    from interfaceSiteProfile import * #@UnusedWildImport
    pass
except ImportError, e:
    pass

# Address Forms

class IGSEmailAddressEntry(Interface):
    email = EmailAddress(title=u'Email Address',
        description=u'Your email address.',
        required=True)

class IGSResendVerification(IGSEmailAddressEntry):
    """Schema use to define the user-interface that the user uses to
    resend his or her verification email, while in the middle of 
    registration."""

class IGSVerifyWait(IGSEmailAddressEntry):
    """Schema use to define the user-interface presented while the user
    waits for verification of his or her email address."""

    came_from = URI(title=u'Came From',
      description=u'The page to return to after retistration has finished',
      required=False)
    
# Registration
class GroupIDNotFound(ValidationError):
    """Group identifier not found"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'Group identifier %s not found' % repr(self.value)
    def doc(self):
        return self.__str__()

class GroupID(ASCIILine):
    def constraint(self, value):
        groupsInfo = createObject('groupserver.GroupsInfo', self.context)
        groupIds = groupsInfo.get_visible_group_ids()
        if value not in groupIds:
            raise GroupIDNotFound(value)
        return True

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
        
    list = ASCIILine(title=u"List",
        description=u'The UL element that lists the widgets.',
        required=False,
        default='')

class IGSAwaitingVerificationJavaScriptContentProvider(IContentProvider):
    pageTemplateFileName = Text(title=u"Page Template File Name",
      description=u'The name of the ZPT file that is used to render the '\
        u'javascript.',
      required=False,
      default=u"browser/templates/verify_wait_javascript.pt")

    email = EmailAddress(title=u'Email Address',
        description=u'Your email address.',
        required=True)

