from zope.component import createObject
import zope.app.pagetemplate.viewpagetemplatefile
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import zope.interface, zope.component, zope.publisher.interfaces
import zope.viewlet.interfaces, zope.contentprovider.interfaces 
from Products.XWFCore import XWFUtils, ODict
from interfaces import *

class GSUserImageContentProvider(object):
    """GroupServer view of the user image
    """

    zope.interface.implements( IGSUserImage )
    zope.component.adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)

    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

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
    def userName(self):
        retval = u''
        retval = XWFUtils.get_user_realnames(self.user)
        return retval
        
    @property
    def userImageUrl(self):
        retval = self.user.get_image() or ''
        assert type(retval) == str
        return retval
        
    @property
    def userImageShow(self):
        retval = self.showImageRegardlessOfUserSetting or \
          getattr(self.user, 'showImage', False)
        assert type(retval) == bool
        return retval

zope.component.provideAdapter(GSUserImageContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.UserImage")

