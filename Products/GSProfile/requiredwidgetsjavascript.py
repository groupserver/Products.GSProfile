# coding=utf-8
from zope.component import createObject
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
import zope.interface, zope.component, zope.publisher.interfaces
import zope.viewlet.interfaces, zope.contentprovider.interfaces 
from interfaces import *

class GSRequiredWidgetsJavaScriptContentProvider(object):
    """Content provider for the required widgets JavaScript."""
    zope.interface.implements( IGSRequiredWidgetsJavaScriptContentProvider )
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

        rws = [w for w in self.widgets if w.required]
        rwIds = ['\'#%s\''%w.name.replace('.','\\\\.') for w in rws]
        self.requiredWidgetsArray = '%s' % ', '.join(rwIds);

    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled

        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self, 
          requiredWidgetsArray=self.requiredWidgetsArray,
          button=self.button)

zope.component.provideAdapter(GSRequiredWidgetsJavaScriptContentProvider,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.RequiredWidgetsJavaScript")

