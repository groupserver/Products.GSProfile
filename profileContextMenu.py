from zope.component import createObject
import zope.app.pagetemplate.viewpagetemplatefile
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import zope.interface, zope.component, zope.publisher.interfaces
import zope.viewlet.interfaces, zope.contentprovider.interfaces 
from Products.XWFCore import XWFUtils, ODict
from interfaces import *


class GSProfileContextMenuContentProvider(object):
    """GroupServer context-menu for the user profile area.
    """

    zope.interface.implements( IGSProfileContextMenuContentProvider )
    zope.component.adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.__pages__ = {
          'edit.html':     'Edit Profile',
          'image.html':    'Edit Image',
          'email.html':    'Edit Email Settings',
          'password.html': 'Set Password'}

        self.context = context
        self.request = request
        
    def update(self):
        self.__updated = True

        self.siteInfo = createObject('groupserver.SiteInfo', 
          self.context)
        self.groupsInfo = createObject('groupserver.GroupsInfo', 
          self.context)

    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)
        
    #########################################
    # Non standard methods below this point #
    #########################################
    @property
    def viewingUser(self):
        assert hasattr(self, 'request')
        assert hasattr(self.request, 'AUTHENTICATED_USER')
        retval = self.request.AUTHENTICATED_USER
        return retval
    @property
    def userName(self):
        retval = u''
        retval = XWFUtils.get_user_realnames(self.context)
        return retval

    @property
    def userId(self):
        userId = self.context.getId()
        return userId
    
    @property
    def userUrl(self):
        retval = '/contacts/%s' % self.userId
        assert type(retval) == str
        assert retval
        return retval

    @property
    def pages(self):
        return self.__pages__
        
    def page_is_current(self, pageId):
        requestBase = self.request.URL.split('/')[-1]
        return requestBase == pageId

    def pageClass(self, pageId):
        if self.page_is_current(pageId):
            retval = 'current'
        else:
            retval = 'not-current'
        assert retval
        return retval

zope.component.provideAdapter(GSProfileContextMenuContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.ProfileContextMenu")

