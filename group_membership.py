# coding=utf-8
from zope.interface import implements, alsoProvides
from zope.component import getUtility, createObject
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from interfaceCoreProfile import IGSJoinableGroups


class JoinableGroupsForSite(object):
    implements(IGSJoinableGroups)
    
    @property
    def groups(self):
        assert self.context
        assert self.user
        assert self.groupsInfo
        
        userId = self.context.getId()
        groups = self.groupsInfo.get_joinable_groups_for_user(userId)
        
        for group in groups:
            g = createObject('groupserver.GroupInfo', group)
            retval = (g.get_id(), g.get_name())
            assert type(retval) == tuple
            assert len(retval == 2)
            yield retval

def joinableGroupsVocabulary(context):
    utility = getUtility(IGSJoinableGroups)
    return SimpleVocabulary.fromItems(utility.groups)
alsoprovides(joinableGroupsVocabulary, IVocabularyFactory)

