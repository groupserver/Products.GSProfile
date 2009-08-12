# coding=utf-8
import pytz
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from interfaceCoreProfile import IGSCoreProfile, display_name_not_nul, \
  deliveryVocab
from emailaddress import EmailAddress

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

########
# ABEL #
########

collegeVocab = SimpleVocabulary([
  SimpleTerm('ca', 'ca',  u'College of Chartered Accountants'),
  SimpleTerm('aca','aca', u'College of Associated Chartered Accountants'), 
  SimpleTerm('at', 'at',  u'College of Accounting Technicians')])

locationVocab = SimpleVocabulary([
  SimpleTerm('n','n', u'Auckland, North of Harbour Bridge'),
  SimpleTerm('a','a', u'Auckland, South of Harbour Bridge'), 
  SimpleTerm('h','h', u'Hamilton'), 
  SimpleTerm('t','t', u'Tauranga'),
  SimpleTerm('p','p', u'Palmerston North'), 
  SimpleTerm('w','w', u'Wellington'), 
  SimpleTerm('c','c', u'Christchurch'), 
  SimpleTerm('d','d', u'Dunedin'),
  SimpleTerm('lon','lon', u'London')])

addressTypeVocab = SimpleVocabulary([
  SimpleTerm('work', 'work',  u'Work'),
  SimpleTerm('home', 'home',  u'Home')])
  
employerClassificationVocab = SimpleVocabulary([
  SimpleTerm('publicPractice_business', 'publicPractice_business',  
             u'Public Practice Business Services'),
  SimpleTerm('publicPractice_audit',    'publicPractice_audit',  
             u'Public Practice Audit'),
  SimpleTerm('publicPractice_tax',      'publicPractice_tax',  
             u'Public Practice Tax'),
  SimpleTerm('publicPractice_other',    'publicPractice_other',  
             u'Public Practice Other'),
  SimpleTerm('corporate',     'corporate',      u'Corporate Sector'),
  SimpleTerm('publicSector',  'publicSector',   u'Public Sector'),
  SimpleTerm('academic',      'academic',       u'Academic'),
  SimpleTerm('notforprofit',  'notforprofit',   u'Not for Profit'),
  SimpleTerm('other',         'other',          u'Other'),])

class IABELProfile(IGSCoreProfile):
    membershipID = TextLine(title=u'NZICA Membership Number',
      description=u'New Zealand Institute of Chartered Accountants '\
        u'Membership Number.',
      required=False)

    candidateID = TextLine(title=u'Candidate Number',
      description=u'ABEL Candidate Number.',
      required=False)
      
    familyName = TextLine(title=u'Family Name',
      description=u'The name inherited by birth, or acquired by marriage.',
      required=False,
      min_length=1,
      constraint=display_name_not_nul)
      
    givenName = TextLine(title=u'Given Names',
      description=u'The name that is given by the parents.',
      required=False,
      min_length=1,
      constraint=display_name_not_nul)
    
    additionalName = TextLine(title=u'Preferred Name',
      description=u'The name that is commonly used in greetings, '\
        u'salutations and felicitations.', 
      readonly=False,
      required=False)
      
    fn = TextLine(title=u'eCampus Display Name',
      description=u'The name seen on the eCampus: on the profile, in '\
        u'correspondence and in posts.',
      required=True,
      min_length=1,
      constraint=display_name_not_nul)

    aliases = Text(title=u'Aliases',
      description=u'Other names.',
      readonly=True,
      required=False)

    gender = Choice(title=u'Gender',
      description=u'The identified gender.',
      default=u'Female',
      vocabulary=SimpleVocabulary.fromValues((u'Female', u'Male')),
      required=False)
      
    tel_work = TextLine(title=u'Work Phone',
      description=u'The telephone number for the place of work',
      required=False)
      
    tel_home = TextLine(title=u'Home Phone',
      description=u'The telephone number for the place of residence',
      required=False)
      
    tel_cell = TextLine(title=u'Cell Phone',
      description=u'The telephone number for the cell phone',
      required=False)

    org = TextLine(title=u'Employer',
      description=u'Company, firm or institution name.',
      required=False)

    adr_type = Choice(title=u'Address Type',
      description=u'Type of address',
      default=u'work',
      vocabulary=addressTypeVocab, 
      required=False)
      
    adr_extended_address = TextLine(title=u'Extended Address',
      description=u'The flat or apartment or office number',
      required=False)

    adr_street_address = TextLine(title=u'Street Address',
      description=u'The street address of the building',
      required=False)

    adr_post_office_box = TextLine(title=u'PO Box',
      description=u'Post Office Box number, or private bag number',
      required=False)

    adr_region = TextLine(title=u'Suburb',
      description=u'The suburb the building is located',
      required=False)
   
    adr_locality = TextLine(title=u'Town or City',
      description=u'The town or city that the suburb is located',
      required=False)

    adr_country = TextLine(title=u'Country',
      description=u'The country the city of town is located',
      required=False,
      default=u'New Zealand')
      
    adr_postal_code = TextLine(title=u'Post Code',
      description=u'The postal code for the address',
      required=False,
      default=u'')

    employer_classification = Choice(title=u'Employer Classification',
      description=u'Employer Classification',
      vocabulary=employerClassificationVocab,
      default='publicPractice_business',
      required=False)

    employer_classification_other = TextLine(
      title=u'Employer Classification (Other)',
      description=u'Employer classification (if Other selected)',
      required=False)

    tertiaryInstitution = TextLine(title=u'Tertiary Institution',
      description=u'Where you completed your academic requirements',
      required=False)

    college = Choice(title=u'College',
      description=u'Intended NZICA College',
      vocabulary=collegeVocab,
      default='ca',
      required=False)
      
    preferredWorkshopLocation = Choice(title=u'Preferred Workshop Location',
      description=u'Where you would like to participate in your workshop',
      vocabulary=locationVocab,
      default='a',
      required=False)
      
    preferredExamLocation = Choice(title=u'Preferred Exam Location',
      description=u'Where you wish to sit your examination.',
      vocabulary='abel.ExamLocations',
      default='a',
      required=False)

    disability = Bool(title=u'Disability',
      description=u'Special support required to participate in the programme.',
      default=False, 
      required=False)
      
    specialDiet = Bool(title=u'Special Dietary Requirements',
      description=u'Special dietary requirements.',
      default=False, 
      required=False)
      
    biography = Text(title=u'Biography',
      description=u'A description detailing life and interests.',
      default=u'', 
      required=False)
      
    tz = Choice(title=u'Timezone',
      description=u'The timezone you wish to use',
      required=True,
      default=u'Pacific/Auckland',
      vocabulary=SimpleVocabulary.fromValues(pytz.common_timezones))

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
    email = EmailAddress(title=u'Email Address',
      description=u'The email address of the new group member.'\
        u'The invitation will be sent to this address, and the address '\
        u'will become the default address for the new group member.',
      required=True)

class IABELProfileAdminJoinSingle(IABELProfileAdminJoin):
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
    email = EmailAddress(title=u'Email Address',
      description=u'The email address of the new group member.'\
        u'The invitation will be sent to this address, and the address '\
        u'will become the default address for the new group member.',
      required=True)

class IDoWireProfileAdminJoinSingle(IDoWireProfileAdminJoin):
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
    email = EmailAddress(title=u'Email Address',
      description=u'The email address of the new group member.'\
        u'The invitation will be sent to this address, and the address '\
        u'will become the default address for the new group member.',
      required=True)

class IEDemProfileAdminJoinSingle(IEDemProfileAdminJoin):
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

class IEDemProfileAdminJoinCSV(IEDemProfileAdminJoin):
    pass

