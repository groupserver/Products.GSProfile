# coding=utf-8
'''Implementation of the Remote Request Registration form.
'''
from Products.Five import BrowserView
from zope.component import createObject
import logging
log = logging.getLogger('GSProfile')

class GSRemoteRequestRegistration(BrowserView):
    '''View object for the GroupServer Remote Request Registration'''
    def __init__(self, context, request):
        log.info('Stuff')
        assert context
        assert request
        self.context = context
        self.request = request
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.groupInfo = createObject('groupserver.GroupInfo', context)
        log.info('Things')

