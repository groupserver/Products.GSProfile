from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.interface import implements, Interface
from zope.component import adapts, createObject, provideAdapter
from zope.contentprovider.interfaces import UpdateNotCalled, IContentProvider
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from Products.XWFCore import XWFUtils
from Products.GSProfile.interfaces import IGSUserImage

class GSUserImageContentProvider(object):
    """GroupServer view of the user image
    """
    implements( IGSUserImage )
    adapts(Interface, IDefaultBrowserLayer, Interface)

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
            raise UpdateNotCalled
        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)
        
    #########################################
    # Non standard methods below this point #
    #########################################

    @property
    def userName(self):
	# check that we aren't dealing with an Anonymous user
        if self.user.getId():
	    retval = XWFUtils.get_user_realnames(self.user)
        else:
            retval = ''
        
        return retval
        
    @property
    def userImageUrl(self):
	# check that we aren't dealing with an Anonymous user
        if self.user.getId():
            retval = self.user.get_image() or ''
        else:
            retval = ''

        return retval
        
    @property
    def userImageShow(self):
        retval = bool(self.userImageUrl) and (
                      self.showImageRegardlessOfUserSetting or
                      getattr(self.user, 'showImage', False))
        assert type(retval) == bool
        return retval

provideAdapter(GSUserImageContentProvider,
    provides=IContentProvider,
    name="groupserver.UserImage")

