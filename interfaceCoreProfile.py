# coding=utf-8
import re, pytz
from string import ascii_letters, digits
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary
from Products.XWFCore import XWFUtils
from emailaddress import EmailAddress

def display_name_not_nul(text):
    retval = text.strip() != u''
    assert type(retval) == bool
    return retval

class IGSCoreProfile(Interface):
    """Schema use to defile the core profile of a GroupServer user."""
    
    fn = TextLine(title=u'Name',
      description=u'The name that you want others to see on your profile '
        u'and posts.',
      required=True,
      min_length=1,
      constraint=display_name_not_nul)

    tz = Choice(title=u'Timezone',
      description=u'The timezone you wish to use',
      required=False,
      default=u'UTC',
      vocabulary=SimpleVocabulary.fromValues(pytz.common_timezones))
    
    biography = Text(title=u'Biography',
      description=u'A desciption of you.',
      required=False,
      default=u'')

class IGSCoreProfileRegister(IGSCoreProfile):
    joinable_groups = List(title=u'Joinable Groups',
      description=u'Groups on this site you can join.',
      required=False,
      value_type=Choice(title=u'Group', vocabulary='JoinableGroups'),
      unique=True,
      default=[])

class IGSCoreProfileAdminJoin(IGSCoreProfile):
    email = EmailAddress(title=u'Email Address',
      description=u'Your email address.',
      required=True)
    # --=mpj17=-- A normal email address field is used, rather than a
    #   *new* email address field, because we want to add users who 
    #   exist on the system :)
    
class IGSCoreProfileAdminJoinSingle(IGSCoreProfileAdminJoin):
    message = Text(title=u'Message',
      description=u'The message to send to the new group member',
      required=False)

class IGSCoreProfileAdminJoinCSV(IGSCoreProfileAdminJoin):
    pass
    
#########
# Image #
#########

class VGSImageWrongType(ValidationError):
    """Verification identifier not found"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        msg = 'The image should be a JPEG (image/jpeg), but it is'
        msg = '%s a %s.' % (msg, repr(self.value))
        return msg
    def doc(self):
        return self.__str__()
class VGSImageWrongWidth(ValidationError):
    """Verification identifier not found"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        msg = 'The image is too wide (%s pixels). ' % repr(self.value)
        msg = '%s Images can only be 150 pixels wide.' % msg
        return msg
    def doc(self):
        return self.__str__()
class VGSImageWrongHeight(ValidationError):
    """Verification identifier not found"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        msg = 'The image is too high (%s pixels). ' % repr(self.value)
        msg = '%s Images can only be 200 pixels high.' % msg
        return msg
    def doc(self):
        return self.__str__()

class GSImage(Bytes):
    def constraint(self, image):
        images = self.context.contactsimages

        tmpImageName = '%s.jpg_temp' % self.context.getId()
        if hasattr(images, tmpImageName):
            context.contactsimages.manage_delObjects([tmpImageName])
        userName = XWFUtils.get_user_realnames(self.context)
        images.manage_addImage(tmpImageName, image, userName)
        
        tmpImage = getattr(images, tmpImageName)
        imageContentType = tmpImage.content_type
        imageWidth = tmpImage.width
        imageHeight = tmpImage.height
        images.manage_delObjects([tmpImageName])
        
        if (imageContentType != 'image/jpeg'):
            raise VGSImageWrongType(imageContentType)
        if (imageWidth > 150):
            raise VGSImageWrongWidth(imageWidth)
        if (imageHeight > 200):
            raise VGSImageWrongHeight(imageHeight)
        return True

class IGSProfileImage(Interface):

    image = GSImage(title=u'Image',
      description=u'The image you want others to see on your profile '
        u'and posts, usually a photograph. The image must be a JPEG, '
        u'no wider than 150 pixels, and no higher than 200 pixels.',
      required=False,
      default=None)
      
    showImage = Bool(title=u'Show Image',
      description=u'If set, others can see your image.',
      required=False,
      default=True)

############
# Nickname #
############

class VInvalidNicnameChar(ValidationError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        msg = 'The character %s is not allowed. '\
          'Nicknames can only contain ASCII letters, digits, '\
          'underscores, and dashes.' % repr(self.value)
        return msg
    def doc(self):
        return self.__str__()

class VNicknameUsed(ValidationError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        msg = 'The nickname %s is already in use.' %\
          repr(self.value)
        return msg
    def doc(self):
        return self.__str__()

class VUserIDUsed(ValidationError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        msg = 'The user-identifier %s is already in use.' %\
          repr(self.value)
        return msg
    def doc(self):
        return self.__str__()


class GSNickname(ASCIILine):
    allowedChars = ascii_letters + digits + '_-'
    def constraint(self, nickname):
        for c in nickname:
            if c not in self.allowedChars:
                raise VInvalidNicnameChar(c)
        if self.context.acl_users.getUser(nickname):
            raise VUserIDUsed(nickname)
        if self.context.acl_users.get_userIdByNickname(nickname):
            raise VNicknameUsed(nickname)
        return True

class IGSSetNickname(Interface):
    nickname = GSNickname(title=u'Nickname',
      description=u'The nickname you wish to set.'\
        u'A nickname can only contain upper or lower case letters, '\
        u'digits, underscores and dahses. A nickname cannot contain '\
        u'spaces, and you cannot have a nickname that is used by anyone '\
        u'else.',
      required=True)
   
#####
    
class IGSCreateUserCSV(Interface):
    csvFile = Bytes(title=u'CSV File',
      description=u'The comma-seperated value file that contains the '
        u'membership information you wish to load.',
      required=True,
      default=None)

