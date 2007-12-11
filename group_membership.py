# coding=utf-8
from zope.interface import implements, alsoProvides
from zope.component import getUtility, createObject
from zope.schema.interfaces import ITokenizedTerm, IVocabulary,\
  IVocabularyTokenized 
from zope.interface.common.mapping import IEnumerableMapping 

class GroupTerm(object):
    implements(ITokenizedTerm)
    def __init__(self, value, token):
        self.value = value
        self.token = token
        
class JoinableGroupsForSite(object):
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context
        self.__userId = context.getId()
        self.__groupsInfo = createObject('groupserver.GroupsInfo', context)
        
        self.__groups = None

    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return iter([GroupTerm(g.get_id(), g.get_name())
                     for g in self.groups])

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.groups)

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = False
        retval = value in [g.get_id() for g in self.groups]
        assert type(retval) == bool
        return retval

    def getQuery(self):
        """See zope.schema.interfaces.IBaseVocabulary"""
        return None

    def getTerm(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        for group in self.groups:
            if group.get_id() == value:
                return GroupTerm(group.get_id(), group.get_name())
        raise LookupError, value

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        for group in self.groups:
            if group.get_name() == token:
                return GroupTerm(group.get_id(), group.get_name())
        raise LookupError, token

    @property
    def groups(self):
        assert self.context
        assert self.__groupsInfo
        
        if self.__groups == None:
            userId = self.context.getId()
            groups = self.__groupsInfo.get_joinable_groups_for_user(self.context)
            self.__groups = [createObject('groupserver.GroupInfo', g)
                             for g in groups]
        assert type(self.__groups) == list
        return self.__groups

