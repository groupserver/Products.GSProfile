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

class GSEmailSettings(BrowserView):
    '''View object for standard GroupServer User-Profile Instances'''
    def __init__(self, context, request):
        assert context
        assert request
        self.context = context
        self.request = request
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', context)
        
        self.__user = self.__get_user()

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
        
    def emailVisibility(self):
        config = self.context.GlobalConfiguration
        retval = config.getProperty('showEmailAddressTo', 'nobody')
        retval = retval.lower()
        assert type(retval) == str
        assert retval
        assert retval in ('nobody', 'request', 'everybody')
        return retval

    def groupMembership(self):
        u = self.__get_user()
        au = self.request.AUTHENTICATED_USER
        authUser = None
        if (au.getId() != None):
            authUser = self.context.site_root().acl_users.getUser(au.getId())
        groups = self.groupsInfo.get_member_groups_for_user(u, authUser)
        retval = [createObject('groupserver.GroupInfo', g) for g in groups]
        assert type(retval) == list
        return retval

    @property
    def userAddresses(self):
        retval = [
          { 'id':       'mpl17atonlinegroups.net',
            'address':  'mpj17@onlinegroups.net',
            'default':  True,
            'verified': True},
          { 'id':       'mpl17atstudent.canterbury.ac.nz',
            'address':  'mpj17@student.canterbury.ac.nz',
            'default':  False,
            'verified': True}]
        assert type(retval) == list
        return retval
        
    @property
    def multipleDefault(self):
        retval = False
        assert type(retval) == bool
        return retval

    @property
    def groupEmailSettings(self):
        g1 = createObject('groupserver.GroupInfo', 
            getattr(self.groupsInfo.groupsObj, 'team'))
        retval = [
          { 'group':      g1,
            'addresses':  ['mpj17@student.canterbury.ac.nz'],
            'setting':    'Email and Web'}]
        assert type(retval) == list
        return retval


    @property
    def supportEmail(self):
        assert type(retval) == str
        retval = ''
        return retval

