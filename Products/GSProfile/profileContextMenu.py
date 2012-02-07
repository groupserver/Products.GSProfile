from zope.component import createObject
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import zope.interface, zope.component, zope.publisher.interfaces
import zope.viewlet.interfaces, zope.contentprovider.interfaces 
from Products.XWFCore import XWFUtils, ODict
from Products.CustomUserFolder.interfaces import IGSUserInfo
from interfaces import *
from zope.app.publisher.browser.menu import getMenu
from AccessControl.security import newInteraction

import logging
log = logging.getLogger('GSProfileContextMenuContentProvider')

class GSProfileContextMenuContentProvider(object):
    """GroupServer context-menu for the user profile area.
    """

    zope.interface.implements(IGSProfileContextMenuContentProvider)
    zope.component.adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request
                
        newInteraction()        

    def update(self):
        self.__updated = True

        self.siteInfo = createObject('groupserver.SiteInfo',
          self.context)
        self.groupsInfo = createObject('groupserver.GroupsInfo',
          self.context)
        self.userInfo = IGSUserInfo(self.context)

        self.pages = getMenu('user_profile_menu', self.context, self.request)

        self.requestBase = self.request.URL.split('/')[-1]
        self.userId = self.context.getId()

    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)
        
    #########################################
    # Non standard methods below this point #
    #########################################
    
    def page_class(self, page):
        if page['selected']:
            retval = 'current'
        else:
            retval = 'not-current'
        assert retval
        return retval

zope.component.provideAdapter(GSProfileContextMenuContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ProfileContextMenu")

