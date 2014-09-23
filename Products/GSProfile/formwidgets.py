#coding: utf-8
from __future__ import absolute_import, unicode_literals
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.component import adapter, provideAdapter
from zope.interface import (implementer, Interface)
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.contentprovider.interfaces import (UpdateNotCalled,
                                             IContentProvider)
from .interfaces import IGSFormWidgets


@implementer(IGSFormWidgets)
@adapter(Interface, IDefaultBrowserLayer, Interface)
class GSFormWidgets(object):
    """The standard layout for GroupServer Form Widgets"""
    def __init__(self, context, request, view):
        self.__parent__ = self.view = view
        self.__updated = False

        self.context = context
        self.request = request

    def update(self):
        self.__updated = True

    def render(self):
        if not self.__updated:
            raise UpdateNotCalled
        pageTemplate = PageTemplateFile(self.pageTemplateFileName)
        return pageTemplate(view=self)

    #########################################
    # Non standard methods below this point #
    #########################################

provideAdapter(GSFormWidgets,
               provides=IContentProvider,
               name="groupserver.FormWidgets")
