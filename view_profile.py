# coding=utf-8
from UserDict import UserDict

import Globals
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import createObject
from zope.interface import implements
from zope.component.interfaces import IFactory
import Products.GSContent.interfaces
from Products.XWFCore import XWFUtils

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
        assert self.request
        assert hasattr(self.request, 'AUTHENTICATED_USER'), \
          'No authenticated user'
        assert self.context
        
        loggedInUser = self.request.AUTHENTICATED_USER
        userId = loggedInUser.getId()
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
    def properties(self):
        assert self.props
        return self.props            
        
    def get_property(self, propertyId, default=''):
        retval = default

        if propertyId in self.props.keys():
            retval = self.__get_user().getProperty(propertyId, default)
            
        return retval

# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747
class ODict(UserDict):
    def __init__(self, dict = None):
        self._keys = []
        UserDict.__init__(self, dict)

    def __delitem__(self, key):
        UserDict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        UserDict.__setitem__(self, key, item)
        if key not in self._keys: self._keys.append(key)

    def clear(self):
        UserDict.clear(self)
        self._keys = []

    def copy(self):
        dict = UserDict.copy(self)
        dict._keys = self._keys[:]
        return dict

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj = None):
        UserDict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dict):
        UserDict.update(self, dict)
        for key in dict.keys():
            if key not in self._keys: self._keys.append(key)

    def values(self):
        return map(self.get, self._keys)

