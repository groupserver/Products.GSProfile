# coding=utf-8
import Globals
import zope.app.apidoc.interface
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import createObject, getUtility
from zope.interface import implements
from zope.interface.interface import InterfaceClass
from zope.component.interfaces import IFactory
from zope.schema.interfaces import IVocabularyFactory
from Products.XWFCore import XWFUtils
from Products.XWFCore.odict import ODict
from Products.CustomUserFolder.interfaces import IGSUserInfo
from gs.profile.email.base.emailuser import EmailUser
from interfaces import *

import logging
log = logging.getLogger('GSProfile')

# TODO: The code for displaying profile properties should be moved from
# the GSProfileView class to a viewlet. The viewlet class would contain
# the get_propery method, and a properties attribute (defined as the
# __properties_dict method below). Skins can define their own viewlet,
# simplifying the code *massively*.

class GSProfileView(BrowserView):
    '''View object for standard GroupServer User-Profile Instances'''
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        self.userInfo = IGSUserInfo(context)
        self.emailUser = EmailUser(context, self.userInfo)
        
        self.props = self.__properties_dict()
        self.__user = self.__get_user()

    def __get_global_config(self):
        site_root = self.context.site_root()
        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        assert config
        return config
        
    def __properties_dict(self):
        retval = ODict()
        config = self.__get_global_config()
        hiddenFields = getattr(config, 'hiddenFields', [])
        
        profileSchema = self.__get_schema()
        ifs = zope.app.apidoc.interface.getFieldsInOrder(profileSchema)
        for interface in ifs:
            if interface[0] not in hiddenFields:
                retval[interface[0]] = interface[1]
        return retval
        
    def __get_schema(self):
        retval = IGSCoreProfile
        config = self.__get_global_config()
        interfaceName = config.getProperty('profileInterface', '')
        site_root = self.context.site_root()
        assert hasattr(site_root, 'GlobalConfiguration')
        config = site_root.GlobalConfiguration
        interfaceName = config.getProperty('profileInterface', '')
        if interfaceName:
            retval = eval(interfaceName)

        assert retval
        assert type(retval) == InterfaceClass
        return retval
        
    def __get_user(self):
        assert self.context
        
        userId = self.context.getId()
        site_root = self.context.site_root()
        assert site_root
        assert hasattr(site_root, 'acl_users'), 'acl_users not found'
        acl_users = site_root.acl_users
        
        user = acl_users.getUserById(userId)
        assert user
        return user
        
    @property
    def properties(self):
        assert self.props
        return self.props            
        
    def get_property(self, propertyId, default=''):
        p = self.props[propertyId].bind(self.context)
        if (hasattr(p, 'vocabulary') and (p.vocabulary == None)):
            # Deal with named vocabularies
            p.vocabulary = getUtility(IVocabularyFactory, \
                p.vocabularyName, self.context)
        r = p.query(self.context, default)
        if  hasattr(p, 'vocabulary'):
            try:
                retval = p.vocabulary.getTerm(r).title
            except LookupError, e:
                retval = r
            except AttributeError, e:
                retval = r
        elif hasattr(p, 'value_type') and type(r) == list:
            # Named vocabularies will cause a mare, like above.
            vocab = p.value_type.vocabulary
            s = [vocab.getTerm(v).title for v in r]
            retval = XWFUtils.comma_comma_and(s)
        else:
            retval = r
            
        return retval
        
    def emailVisibility(self):
        config = self.context.GlobalConfiguration
        retval = config.getProperty('showEmailAddressTo', 'nobody')
        retval = retval.lower()
        assert type(retval) == str
        assert retval
        assert retval in ('nobody', 'request', 'everybody')
        return retval

    def userEmailAddresses(self):
        retval = self.emailUser.get_addresses()
        assert type(retval) == list
        assert retval
        return retval

    def groupMembership(self):
        u = self.__get_user()
        au = self.request.AUTHENTICATED_USER
        authUser = None
        if (au.getId() != None):
            authUser = self.context.site_root().acl_users.getUser(au.getId())
        groups = self.groupsInfo.get_member_groups_for_user(u, authUser)
        retval = [createObject('groupserver.GroupInfo', g) for g in groups]
        retval.sort(groupInfoSorter)
        assert type(retval) == list
        return retval

def groupInfoSorter(a, b):
    # TODO: Move to Group Membership
    assert hasattr(a, 'name')
    assert hasattr(b, 'name')

    aname = a.name.lower()
    bname = b.name.lower()
    if (aname < bname):
        retval = -1
    elif (aname == bname):
        retval = 0
    else: # aname > bname
        retval = 1
    
    assert retval in (-1, 0, 1)
    return retval

