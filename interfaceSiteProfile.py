# coding=utf-8
import pytz
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary
from interfaceCoreProfile import IGSCoreProfile, display_name_not_nul
from interfaceCoreProfile import deliveryChoice, invitationMessageText,\
  adminNewUserEmail


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
      
    url = URI(title=u'Personal URL',
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
      
    org_url = URI(title=u'Organisation Website',
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
    email = adminNewUserEmail

class IOGNProfileAdminJoinSingle(IOGNProfileAdminJoin):
    message = invitationMessageText      
    delivery = deliveryChoice

class IOGNProfileAdminJoinCSV(IOGNProfileAdminJoin):
    pass

########
# ABEL #
########

class IABELProfile(IGSCoreProfile):
    fn = TextLine(title=u'Display Name',
      description=u'The name that everyone will see on your profile '
        u'and posts.',
      required=True,
      min_length=1,
      constraint=display_name_not_nul,
      readonly=True)

    givenName = TextLine(title=u'First Name',
      description=u'The name that you are commonly called, that is given '
        u'to you by your parents.',
      required=True,
      min_length=1,
      constraint=display_name_not_nul,
      readonly=True)
    
    familyName = TextLine(title=u'Last Name',
      description=u'The name that you inherit by birth, or aquire by '
        u'marrage.',
      required=True,
      min_length=1,
      constraint=display_name_not_nul,
      readonly=True)
      
    biography = Text(title=u'Biography',
      description=u'A desciption of you.',
      required=False,
      default=u'')
      
    tz = Choice(title=u'Timezone',
      description=u'The timezone you wish to use',
      required=False,
      default=u'UTC',
      vocabulary=SimpleVocabulary.fromValues(pytz.common_timezones))

    region = TextLine(title=u'Preferred Workshop Location',
      description=u'Where you would prefer to attend workshops.',
      required=True,
      readonly=True)

    org = TextLine(title=u'Employer',
      description=u'The organisation that employs you.',
      required=True,
      readonly=True)

    employment_category = TextLine(title=u'Employment Category',
      description=u'The area of accountancy that you work in',
      required=True,
      readonly=True)

    membershipID = TextLine(title=u'NZICA Membership Number',
      description=u'Your New Zealand Institute of Chartered Accountants Membership Number',
      required=False,
      readonly=True)

    candidateID = TextLine(title=u'Candidate Number',
      description=u'Your ABEL Candidate Number',
      required=False,
      readonly=True)
      
    eminervaID = TextLine(title=u'eMinerva ID',
      description=u'The identifier for your record in the eMinerva Student Control System',
      required=False,
      readonly=True)

    preferredExamLocation = TextLine(title=u'Preferred Examination Location',
      description=u'Where you wish to sit your exam.',
      required=False,
      readonly=True)

class IABELProfileRegister(IABELProfile):
    joinable_groups = List(title=u'Joinable Groups',
      description=u'Groups on this site you can join.',
      required=False,
      value_type=Choice(title=u'Group', vocabulary='JoinableGroups'),
      unique=True,
      default=[])

    came_from = URI(title=u'Came From',
      description=u'The page to return to after retistration has finished',
      required=False)
    
class IABELProfileAdminJoin(IABELProfile):
    email = adminNewUserEmail

class IABELProfileAdminJoinSingle(IABELProfileAdminJoin):
    message = invitationMessageText
    delivery = deliveryChoice
    
class IABELProfileAdminJoinCSV(IABELProfileAdminJoin):
    pass

##########
# DoWire #
##########

imClients = [u'Skype', u'Yahoo!', u'ICQ', u'MSN', u'AIM',
  u'Google Talk', u'Gizmo', u'IRC']

class IDoWireProfile(IGSCoreProfile):
    
    fn = TextLine(title=u'Name',
      description=u'The name that you want others to see on your profile '
        u'and posts.',
      required=True,
      min_length=1,
      constraint=display_name_not_nul)
      
    givenName = TextLine(title=u'First Name',
      description=u'The name that you are commonly called, that is given '
        u'to you by your parents.',
      required=False)
    
    familyName = TextLine(title=u'Last Name',
      description=u'The name that you inherit by birth, or aquire by '
        u'marrage.',
      required=False)
    
    biography = Text(title=u'Biography',
      description=u'A desciption of you.',
      required=False,
      default=u'')

    whatsNew = Text(title=u"What's New",
      description=u"What is new with your projects, research, etc. "
        u'with most recent at the top.',
      required=False,
      default=u'')
    
    topicsOfInterest = Text(title=u'Topics of Interest',
      description=u'Keywords of topics you are interested in',
      required=False,
      default=u'')

    articles = Text(title=u'Recent Articles',
      description=u'List your recent articles, books, presentations '
        u'about e-democracy, e-government, democracy, etc. with links '
        u'if available.',
      required=False,
      default=u'')

    tz = Choice(title=u'Timezone',
      description=u'The timezone you wish to use',
      required=False,
      default=u'UTC',
      vocabulary=SimpleVocabulary.fromValues(pytz.common_timezones))

    region = TextLine(title=u'City',
      description=u'The area where you live.',
      required=False,
      default=u'')

    locality = TextLine(title=u'State or Province',
      description=u'The state or province you live in.',
      required=False,
      default=u'')
      
    countryName = TextLine(title=u'Country',
      description=u'The country where you live.',
      required=False,
      default=u'')

    tel = ASCIILine(title=u'Telephone Number',
      description=u'Your telephone number (including the country code).',
      required=False,
      default='')

    tel_cell = ASCIILine(title=u'Telephone Number (Cell or Mobile)',
      description=u'Your telephone number (including the country code) '
        u'for your cellular telephone or mobile.',
      required=False,
      default='')

    url = URI(title=u'Your Website',
      description=u'The URL for your website, or page on the Web.',
      required=False)
    
    weblog = URI(title=u'Weblog URL',
      description=u'The location of your weblog (blog).',
      required=False)

    weblog_feed = URI(title=u'Weblog Web Feed',
      description=u'The location of your weblog web-feed.',
      required=False)

    linkedin_url = URI(title=u'LinkedIn URL',
      description=u'The URL of your LinkedIn profile page.',
      required=False)

    delicious_url = URI(title=u'Del.icio.us or FURL Links',
      description=u'The URLs of your Del.icio.us or FURL pages.',
      required=False)

    primaryIMClient = Choice(title=u'Primary IM Client',
      description=u'The instant messaging (IM) client you use most often.',
      vocabulary=SimpleVocabulary.fromValues(imClients),
      required=False)

    primaryIMClient_uid = TextLine(title=u'Primary IM Client User ID',
      description=u'The user ID (user name) you use with your primary IM '
        u'client.',
      required=False,
      default=u'')
    
    secondaryIMClient = Choice(title=u'Secondary IM Client',
      description=u'The other instant messaging (IM) client you use '
        u'frequently.',
      vocabulary=SimpleVocabulary.fromValues(imClients),
      required=False)

    secondaryIMClient_uid = TextLine(title=u'Secondary IM Client User ID',
      description=u'The user ID (user name) you use with your other IM '
        u'client.',
      required=False,
      default=u'')

    org = TextLine(title=u'Organisation',
      description=u'The organisation that you are primarily engaged with.',
      required=False,
      default=u'')

    org_type = TextLine(title=u'Organisation Type',
      description=u'The type organisation that you are primarily engaged '
        u'with.', 
      required=False,
      default=u'')
    
    org_url = URI(title=u'Organisation Website',
      description=u'The Web page for your organisation.',
      required=False)

    role = TextLine(title=u'Position',
      description=u'Your position, or title, within your organization.',
      required=False,
      default=u'')

    language = TextLine(title=u'Languages Spoken',
      description=u'The languages you can hold a conversation in.',
      required=False,
      default=u'')

    postal_adr = TextLine(title=u'Postal Address',
      description=u'Your address where you receive mail',
      required=False,
      default=u'')

class IDoWireProfileRegister(IDoWireProfile):
    joinable_groups = List(title=u'Joinable Groups',
      description=u'Groups on this site you can join.',
      required=False,
      value_type=Choice(title=u'Group', vocabulary='JoinableGroups'),
      unique=True,
      default=[])

    came_from = URI(title=u'Came From',
      description=u'The page to return to after retistration has finished',
      required=False)
    

class IDoWireProfileAdminJoin(IDoWireProfile):
    email = adminNewUserEmail

class IDoWireProfileAdminJoinSingle(IDoWireProfileAdminJoin):
    message = invitationMessageText
    delivery = deliveryChoice
    
class IDoWireProfileAdminJoinCSV(IDoWireProfileAdminJoin):
    pass

########
# eDem #
########

class IEDemProfile(IGSCoreProfile):
    givenName = TextLine(title=u'First Name',
      description=u'The name that you are commonly called, which is given '
        u'to you by your parents.',
      required=True)
    
    familyName = TextLine(title=u'Last Name',
      description=u'The name that you inherit by birth, or acquire by '
        u'marriage.',
      required=True)
    
    fn = TextLine(title=u'Display Name',
      description=u'The name that you want others to see. This is usually ' 
        u'your first name followed by your last name.',
      required=True,
      min_length=1,
      constraint=display_name_not_nul)
      
    biography = Text(title=u'Biography',
      description=u'A description of you.',
      required=False,
      default=u'')

    tz = Choice(title=u'Timezone',
      description=u'The timezone you wish to use',
      required=False,
      default=u'UTC',
      vocabulary=SimpleVocabulary.fromValues(pytz.common_timezones))

    neighbourhood = TextLine(title=u'Neighbourhood',
      description=u'The neighbourhood or village where you live.',
      required=False,
      default=u'')

    region = TextLine(title=u'City or Local Authority',
      description=u'The area where you live.',
      required=False,
      default=u'')

    locality = TextLine(title=u'State or Province',
      description=u'The state or province you live in.',
      required=False,
      default=u'')
      
    countryName = TextLine(title=u'Country',
      description=u'The country where you live.',
      required=False,
      default=u'')

    url = URI(title=u'Personal Website or Blog URL',
      description=u'The URL for your website, or weblog.',
      required=False)

    org = TextLine(title=u'Organisation',
      description=u'The organisation that you are primarily engaged with.',
      required=False,
      default=u'')

    org_url = URI(title=u'Organisation Website',
      description=u'The Web page for your organisation.',
      required=False)

    tel = ASCIILine(title=u'Telephone Number (Hidden)',
      description=u'Your telephone number (including the country code). '\
       u'The phone number is required by some groups for admin purposes, '\
       u'but it is only shown to the site-administrators of '\
       u'e-democracy.org. Contact your forum manager for more information.',
      required=False,
      default='')

    streetAddress = TextLine(title=u'Street Address (Hidden)',
      description=u'Your street address. '\
       u'The street address number is required by some groups for admin '\
       u'purposes, but it is only shown to the site-administrators of '\
       u'e-democracy.org. Contact your forum manager for more information.',
      required=False,
      default=u'')

class IEDemProfileRegister(IEDemProfile):
    joinable_groups = List(title=u'Joinable Groups',
      description=u'Groups on this site you can join.',
      required=False,
      value_type=Choice(title=u'Group', vocabulary='JoinableGroups'),
      unique=True,
      default=[])

    came_from = URI(title=u'Came From',
      description=u'The page to return to after retistration has finished',
      required=False)
    
class IEDemProfileAdminJoin(IEDemProfile):
    email = adminNewUserEmail

class IEDemProfileAdminJoinSingle(IEDemProfileAdminJoin):
    delivery = deliveryChoice
    message = invitationMessageText

class IEDemProfileAdminJoinCSV(IEDemProfileAdminJoin):
    pass

