# coding=utf-8
'''Create Users from CSV file.
'''
from zope.component import createObject
from zope.interface import implements, providedBy
from zope.app.apidoc.interface import getFieldsInOrder
from zope.schema import *
from zope.schema.vocabulary import SimpleTerm
from zope.schema.interfaces import ITokenizedTerm, IVocabulary,\
  IVocabularyTokenized, ITitledTokenizedTerm
from zope.interface.common.mapping import IEnumerableMapping 
from Products.Five import BrowserView
from Products.XWFCore.odict import ODict
import interfaces, utils

import logging
log = logging.getLogger('GSCreateUsersFromCSV')

class CreateUsersForm(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.profileList = ProfileList(context)
        
    @property
    def columns(self):
        retval = []
        
        profileAttributes = {}
        for pa in self.profileList:
            profileAttributes[pa.token] = pa.title
        
        for i in range(0, len(self.profileList)):
            j = i + 1
            columnId = 'column%2d' % j
            columnTitle = u'Column %d'% j
            column = {
              'columnId':    columnId, 
              'columnTitle': columnTitle, 
              'profileList': self.profileList}
            retval.append(column)
        assert len(retval) > 0
        return retval
        
        
        
class ProfileList(object):
    implements(IVocabulary, IVocabularyTokenized)
    __used_for__ = IEnumerableMapping

    def __init__(self, context):
        self.context = context
        self.__properties = ODict()

        site_root = context.site_root()

        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        
        profileSchemaName = config.getProperty('profileInterface',
                                              'IGSCoreProfile')
        profileSchemaName = '%sAdminJoinCSV' % profileSchemaName
        assert hasattr(interfaces, profileSchemaName), \
            'Interface "%s" not found.' % profileSchemaName
        self.__schema = getattr(interfaces, profileSchemaName)
        
    def __iter__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        retval = [SimpleTerm(p, p, self.properties[p])
                  for p in self.properties.keys()]
        for term in retval:
              assert term
              assert ITitledTokenizedTerm in providedBy(term)
              assert term.token == term.value
        return iter(retval)

    def __len__(self):
        """See zope.schema.interfaces.IIterableVocabulary"""
        return len(self.properties)

    def __contains__(self, value):
        """See zope.schema.interfaces.IBaseVocabulary"""
        retval = False
        retval = value in self.properties
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
        for p in self.properties:
            if p == token:
                retval = SimpleTerm(p, p, self.properties[p])
                assert retval
                assert ITitledTokenizedTerm in providedBy(retval)
                assert retval.token == retval.value
                return retval
        raise LookupError, token

    @property
    def properties(self):
        assert self.context
        if len(self.__properties) == 0:
            ifs = getFieldsInOrder(self.__schema)
            for interface in ifs:
                self.__properties[interface[0]] = interface[1].title
        retval = self.__properties
        assert isinstance(retval, ODict)
        assert retval
        return retval

