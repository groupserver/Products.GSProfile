# coding=utf-8
from zope.component import createObject
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserPage
from zope.interface import implements
from Products.Five import BrowserView
from zExceptions import NotFound
from interfaces import IGSUserProfiles
from utils import escape_c

import logging
log = logging.getLogger('GSUserProfiles')

def ec(name):
    return ''.join([ord(d) > 127 and hex(ord(d)).replace('0x', r'%') or d
                   for d in name])
# --=mpj17=-- TODO: rewrite this redirector, and the profile-view, to
# behave a lot more like the topics, posts, and images.
class GSUserProfiles(BrowserView):
    implements(IGSUserProfiles, IPublishTraverse, IBrowserPage)
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.__loggedInUser = None
        self.acl_users = context.acl_users
        self.traverse_subpath = []

    def browserDefault(self, request):
        return self, ()
    
    def publishTraverse(self, request, name):
        retval = None
        u1 = self.context.acl_users.getUser(name)
        ec_name = ec(name)
        u2 = self.context.acl_users.get_userByNickname(ec_name)
        user = (u1 or u2)
        if user:
            cnn = user.get_canonicalNickname()
            if cnn == ec(name):
                retval = user            
            else:       
                url = '/p/%s/' % cnn
                self.request.response.redirect(url)
        else:
            m = "No user with the nickname %s" % ec(name)
            log.info(m)
                   
            raise NotFound, m
   
        return retval

    @property
    def loggedInUser(self):
        if self.__loggedInUser == None:
            self.__loggedInUser = createObject('groupserver.LoggedInUser', 
                                    self.context)
        return self.__loggedInUser

    def __call__(self):
        if self.loggedInUser.anonymous:
            uri = '/login.html?came_from=/p'
        else:
            uri = self.loggedInUser.url
        return self.request.RESPONSE.redirect(uri)

