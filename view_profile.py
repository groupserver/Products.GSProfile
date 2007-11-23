# coding=utf-8
import Globals
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import createObject
from zope.interface import implements
from zope.component.interfaces import IFactory
import Products.GSContent.interfaces
from Products.XWFCore import XWFUtils
from Products.XWFCore.odict import ODict

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
        
    def __properties_dict(self):
        retval = ODict()
        retval['displayName'] = 'Display Name'
        retval['nickname'] = 'Nickname'
        retval['timezone'] = 'Timezone'
        retval['biography'] = 'Biography'

        site_root = self.context.site_root()
        assert hasattr(site_root, 'UserProperties')
        siteUserProperties = site_root.UserProperties
        for prop in siteUserProperties.objectValues():
            retval[prop.getId()] = prop.title_or_id()
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
        retval = XWFUtils.get_user_realnames(self.__get_user())

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
        retval = default

        if propertyId in self.props.keys():
            retval = self.__get_user().getProperty(propertyId, default)
            
        return retval

    @property
    def userImageUrl(self):
        retval = self.__get_user().get_image()
        assert type(retval) == str
        return retval
        

