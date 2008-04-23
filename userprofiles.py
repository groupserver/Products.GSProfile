# coding=utf-8
from zope.publisher.interfaces import IPublishTraverse
from zope.app.publisher.browser import queryDefaultViewName
from zope.interface import implements
from Products.Five import BrowserView

from zope.publisher.interfaces.browser import IBrowserView

from zope.publisher.interfaces.browser import IBrowserPublisher 

from zope.component import getMultiAdapter, getAdapter, ComponentLookupError

from Acquisition import aq_inner, aq_base, aq_chain

from zExceptions import NotFound

from interfaces import IGSUserProfiles
from utils import escape_c

import logging
log = logging.getLogger('GSUserProfiles')

def ec(name):
    return ''.join([ord(d)>127 and hex(ord(d)).replace('0x', r'%') or d
                   for d in name])

class GSUserProfiles(BrowserView):
    implements(IGSUserProfiles, IPublishTraverse)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        self.acl_users = context.acl_users
        
        self.traverse_subpath = []
    
    def publishTraverse(self, request, name):
        retval = None
        
        user = (self.context.acl_users.getUser(name) or
                self.context.acl_users.get_userByNickname(ec(name)))

        if user:
            cnn = user.get_canonicalNickname()
            if cnn == ec(name):
                retval = user            
                log.info("Found user with nickname %s" % cnn)
            else:       
                url = '/p/%s/' % cnn
                retval = self.request.response.redirect(url)
        else:
            m  = "No user with the nickname %s" % cnn
            log.info(m)
                   
            raise NotFound, m
   
        assert retval != None
        return retval



