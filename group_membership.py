# coding=utf-8
from zope.interface import implements, alsoProvides, providedBy
from zope.component import getUtility, createObject
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import ITokenizedTerm, IVocabulary,\
  IVocabularyTokenized, ITitledTokenizedTerm
from zope.interface.common.mapping import IEnumerableMapping 

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
        retval = [SimpleTerm(g.get_id(), g.get_id(), g.get_name())
                  for g in self.groups]
        for term in retval:
            assert term
            assert ITitledTokenizedTerm in providedBy(term)
            assert term.token == term.value
        return iter(retval)

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
        return self.getTermByToken(value)
        
    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        for g in self.groups:
            if g.get_id() == token:
                retval = SimpleTerm(g.get_id(), g.get_id(), g.get_name())
                assert retval
                assert ITitledTokenizedTerm in providedBy(retval)
                assert retval.token == retval.value
                return retval
        raise LookupError, token

    @property
    def groups(self):
        assert self.context
        assert self.__groupsInfo
        
        if self.__groups == None:
            userId = self.context.getId()
            gs = self.__groupsInfo.get_joinable_groups_for_user(self.context)
            self.__groups = [createObject('groupserver.GroupInfo', g)
                             for g in gs]
        assert type(self.__groups) == list
        return self.__groups

