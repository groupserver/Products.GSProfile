# coding=utf-8
import re, pytz
from string import ascii_letters, digits
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.XWFCore import XWFUtils
from emailaddress import EmailAddress
from OFS.Image import Image

def display_name_not_nul(text):
    retval = text.strip() != u''
    assert type(retval) == bool
    return retval

deliveryVocab = SimpleVocabulary([
  SimpleTerm('email', 'email',  u'One email per post.'),
  SimpleTerm('digest','digest', u'Daily digest of topics.'), 
  SimpleTerm('web',   'web',    u'Web only.')])

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
    came_from = URI(title=u'Came From',
      description=u'The page to return to after retistration has finished',
      required=False)
    
class IGSCoreProfileAdminJoin(IGSCoreProfile):
    toAddr = EmailAddress(title=u'Email To',
      description=u'The email address of the new group member.'\
        u'The invitation will be sent to this address, and the address '\
        u'will become the default address for the new group member.',
      required=True)

class IGSCoreProfileAdminJoinSingle(IGSCoreProfileAdminJoin):
    message = Text(title=u'Invitation Message',
        description=u'The message that appears at the top of the email '\
            u'invitation to the new group member. The message will '\
            u'appear before the two links that allow the user to accept '\
            u'or reject the inviation.',
        required=True)
    
    fromAddr = Choice(title=u'Email From',
      description=u'The email address that you want in the "From" '\
        u'line in the invitation tat you send.',
      vocabulary = 'EmailAddressesForLoggedInUser',
      required=True)

    delivery = Choice(title=u'Group Message Delivery Settings',
      description=u'The message delivery settings for the new user',
      vocabulary=deliveryVocab,
      default='email')

    subject = TextLine(title=u'Subject',
        description=u'The subject line of the invitation message that '\
            u'will be sent to the new member',
        required=True)    

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

class GSImage(Bytes):
    def constraint(self, image):
        tmpImageName = '%s.jpg_temp' % self.context.getId()
        
        tmpImage = Image(tmpImageName, tmpImageName, image)        
        
        imageContentType = tmpImage.content_type
        imageWidth = tmpImage.width
        imageHeight = tmpImage.height
        
        if (imageContentType != 'image/jpeg'):
            raise VGSImageWrongType(imageContentType)
        return True

class IGSProfileImage(Interface):

    image = GSImage(title=u'Image',
      description=u'The image you want others to see on your profile '
        u'and posts, usually a photograph. The image must be a JPEG.',
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

class IGSRequestContact(Interface):
    pass

