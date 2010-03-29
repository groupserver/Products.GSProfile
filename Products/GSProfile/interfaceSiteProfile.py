# coding=utf-8
from zope.schema import *
from interfaceCoreProfile import IGSCoreProfile, deliveryVocab
from emailaddress import EmailAddress
from saneuri import SaneURI

class IOGNProfile(IGSCoreProfile):
    """Profile for a user of OnlineGroups.Net
    """
    primary_language = TextLine(title=u'Primary Language',
      description=u'Your primary spoken language.',
      required=False,
      default=u'')
      
    city = TextLine(title=u'City/Locality',
      description=u'The city or locality that you live in.',
      required=False,
      default=u'')
      
    country = TextLine(title=u'Country',
      description=u'The country you work in.',
      required=False,
      default=u'')
      
    url = SaneURI(title=u'Personal URL',
      description=u'Your personal website, blog or podcast URL.',
      required=False)
      
    skypeId = TextLine(title=u'Skype User ID',
      description=u'The user ID you use for Skype, if you use Skype.',
      required=False,
      default=u'')
      
    org = TextLine(title=u'Organisation',
      description=u'The organisation that you are involved with.',
      required=False,
      default=u'')
      
    org_url = SaneURI(title=u'Organisation Website',
      description=u'URL for the organisation you are involved with.',
      required=False)
      
    org_role = TextLine(title=u'Roles',
      description=u'Your roles in organisations and the world.',
      required=False,
      default=u'')

class IOGNProfileRegister(IOGNProfile):
    joinable_groups = List(title=u'Joinable Groups',
      description=u'Groups on this site you can join.',
      required=False,
      value_type=Choice(title=u'Group', vocabulary='JoinableGroups'),
      unique=True,
      default=[])

    came_from = URI(title=u'Came From',
      description=u'The page to return to after retistration has finished',
      required=False)
    

class IOGNProfileAdminJoin(IOGNProfile):
    email = EmailAddress(title=u'Email Address',
      description=u'The email address of the new group member.'\
        u'The invitation will be sent to this address, and the address '\
        u'will become the default address for the new group member.',
      required=True)

class IOGNProfileAdminJoinSingle(IOGNProfileAdminJoin):
    message = Text(title=u'Invitation Message',
      description=u'The message that appears at the top of the email '\
        u'invitation to the new group member. The message will appear before '\
        u'the two links that allow the user to accept or reject the '\
        u'inviation.',
        required=False)

    delivery = Choice(title=u'Group Message Delivery Settings',
      description=u'The message delivery settings for the new user',
      vocabulary=deliveryVocab,
      default='email')

class IOGNProfileAdminJoinCSV(IOGNProfileAdminJoin):
    pass

