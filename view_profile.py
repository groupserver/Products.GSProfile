# coding=utf-8
import Globals
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import createObject
from zope.interface import implements
from zope.interface.interface import InterfaceClass
from zope.component.interfaces import IFactory
import Products.GSContent.interfaces
from Products.XWFCore import XWFUtils
from Products.XWFCore.odict import ODict
import zope.app.apidoc.interface # 

from interfaces import *

class GSProfileView(BrowserView):
    '''View object for standard GroupServer User-Profile Instances'''
    def __init__(self, context, request):
        assert context
        assert request
        self.context = context
        self.request = request
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        
        self.props = self.__properties_dict()
        self.__user = self.__get_user()
        
    def __properties_dict(self):
        retval = ODict()
        profileSchema = self.__get_schema()
        ifs = zope.app.apidoc.interface.getFieldsInOrder(profileSchema)
        for interface in ifs:
            retval[interface[0]] = interface[1]
        return retval
        
    def __get_schema(self):
        retval = IGSCoreProfile
        
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
    def userName(self):
        retval = u''
        retval = XWFUtils.get_user_realnames(self.__user)

        return retval

    @property
    def userId(self):
        userId = self.context.getId()
        return userId
    
    @property
    def properties(self):
        assert self.props
        return self.props            
        
    def get_property(self, propertyId, default=''):
        return self.props[propertyId].query(self.__user, default)

    @property
    def userUrl(self):
        retval = '/contacts/%s' % self.userId
        assert type(retval) == str
        assert retval
        return retval

    @property
    def userImageUrl(self):
        retval = self.__user.get_image()
        assert type(retval) == str
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
        retval = self.__user.get_emailAddresses()
        assert type(retval) == list
        assert retval
        return retval


    def groupMembership(self):
        u = self.__get_user()
        authU = self.request.AUTHENTICATED_USER
        groups = self.groupsInfo.get_member_groups_for_user(u, authU)
        retval = [createObject('groupserver.GroupInfo', g) for g in groups]
        assert type(retval) == list
        return retval

