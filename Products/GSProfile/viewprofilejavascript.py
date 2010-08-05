from zope.component import createObject
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import zope.interface, zope.component, zope.publisher.interfaces
from zope.contentprovider.interfaces import UpdateNotCalled, IContentProvider
from Products.CustomUserFolder.interfaces import IGSUserInfo
from interfaces import IGSViewProfileJavaScriptContentProvider

class GSViewProfileJavaScriptContentProvider(object):
    """Content provider for the JavaScript used on profile pages.
    """

    zope.interface.implements(IGSViewProfileJavaScriptContentProvider)
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
        self.userInfo = IGSUserInfo(self.context)

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)

zope.component.provideAdapter(GSViewProfileJavaScriptContentProvider,
    provides=IContentProvider,
    name="groupserver.ViewProfileJavaScript")

