# coding=utf-8
from zope.app.traversing.interfaces import TraversalError, ITraversable
from Products.Five.traversable import Traversable
from zope.interface import implements

from interfaces import IGSUserProfiles
from Products.Five import BrowserView

import logging
log = logging.getLogger('GSUserProfiles')

class GSUserProfiles(BrowserView, Traversable):
    implements(ITraversable, IGSUserProfiles)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
        self.acl_users = context.acl_users
        assert self.acl_users
            
    def traverse(self, name, furtherPath):
        """Get the next item on the path

        Should return the item corresponding to 'name' or raise
        TraversalError where appropriate.

        furtherPath is a list of names still to be traversed. This method is
        allowed to change the contents of furtherPath.

        """
        assert name
        retval = None

        user = self.acl_users.getUser(name)
        if user:
            #m = 'Found user with the ID %s: %s' %\
            #  (name, user.getProperty('fn', ''))
            #log.info(m)
            retval = user
        else:
            user = self.acl_users.get_userByNickname(name)
            if user:
                #m = 'Found user with the nickname %s: %s' %\
                #  (name, user.getProperty('fn', ''))
                log.info(m)
                
                cnn = user.get_canonicalNickname()
                if cnn == name:
                    retval = user
                else:
                    url = '/p/%s/' % cnn
                    #m = 'Redirecting to %s for user %s (%s)' %\
                    #  (url, user.getProperty('fn', ''), user.getId())
                    #log.info(m)
                    r = self.request.RESPONSE.redirect(url)
                    return r
            else:
                m = 'No user with the ID or nickname %s' % name
                log.info(m)
                raise TraversalError

        assert retval != None
        return retval

