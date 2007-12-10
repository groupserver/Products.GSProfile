# coding=utf-8
import re, pytz
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *
from zope.schema.vocabulary import SimpleVocabulary

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

    image = Bytes(title=u'Image',
      description=u'The image you want others to see on your profile '
        u'and posts. It is usually a photograph.',
      required=False)
      
    nickname = DottedName(title=u'Nickname',
      description=u'The name you wish to give your profile. It should be '
        u'a short name, that contains just letters or numbers. If you do '
        u'not set a nickname, one will be created from your display name.',
      required=False,
      min_length=1)

    tz = Choice(title=u'Timezone',
      description=u'The timezone you wish to use',
      required=False,
      default=u'UTC',
      vocabulary=SimpleVocabulary.fromValues(pytz.common_timezones))
    
    biography = Text(title=u'Biography',
      description=u'A desciption of you.',
      required=False)
      
    # groupMembership = List(text=u'Group Membership'
    #  description=u'The groups that you belong to'
    #  required=False,
    #  unique=True,
    #  value_type=Choice())

    #jonableGroups = Set(text=u'Joinable Groups',
    #  description=u'The groups you can join.',
    #  required=False,
    #  unique=True,
    #  value_type=Choice(title=u'Group', vocabulary=u'Joinable Groups'))

class IGSGroupMembership(Interface):
    groups = Iterable(title=u'Group Membership.',
      description=u'The groups that you belong to.')

class IGSJoinableGroups(Interface):
    groups = Iterable(title=u'Joinable Groups',
      description=u'The list of groups on this site')

