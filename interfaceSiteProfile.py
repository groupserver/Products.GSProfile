# coding=utf-8
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary

from interfaceCoreProfile import IGSCoreProfile

class IOGNProfile(IGSCoreProfile):

    primary_language = TextLine(title=u'Primary Language',
      description=u'Your primary spoken language.',
      required=False)
      
    city = TextLine(title=u'City/Locality',
      description=u'The city or locality that you live in.',
      required=False)
      
    country = TextLine(title=u'Country',
      description=u'The country you work in.',
      required=False)
      
    url = URI(title=u'Personal URL',
      description=u'Your personal website, blog or podcast URL.',
      required=False)
      
    skypeId = TextLine(title=u'Skype User ID',
      description=u'The user ID you use for Skype, if you use Skype.',
      required=False)
      
    org = TextLine(title=u'Organisation',
      description=u'The organisation that you are involved with.',
      required=False)
      
    org_url = URI(title=u'Organisation Website',
      description=u'URL for the organisation you are involved with.',
      required=False)
      
    org_role = TextLine(title=u'Roles',
      description=u'Your roles in organisations and the world.',
      required=False)

