#coding: utf-8
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.component import adapts, provideAdapter
import zope.interface
import zope.publisher.interfaces
import zope.contentprovider.interfaces 
from Products.XWFCore import XWFUtils, ODict
from interfaces import *

class GSFormWidgets(object):
    """The standard layout for GroupServer Form Widgets
    """

    zope.interface.implements( IGSFormWidgets )
    adapts(zope.interface.Interface,
        zope.publisher.interfaces.browser.IDefaultBrowserLayer,
        zope.interface.Interface)
    
    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request
        
    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise interfaces.UpdateNotCalled
        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)
        
    #########################################
    # Non standard methods below this point #
    #########################################

provideAdapter(GSFormWidgets,
    provides=zope.contentprovider.interfaces.IContentProvider,
    name="groupserver.FormWidgets")

