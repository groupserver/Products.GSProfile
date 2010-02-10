# coding=utf-8
'''
========================
A Sane URI Schema Field
=======================

The sane URI schema field is like the standard Zope URI field, but it is
far more tolerant of poor input. It is not unheard of for users of a
system to enter ``groupserver.org`` as a URI, rather than 
``http://groupserver.org``.

The users are fools, how dear they fail to follow `RFC2396 
<http://www.ietf.org/rfc/rfc2396.txt>`_ to the letter!
'''
from urlparse import urlparse # Use urlparse to parse urls. Shock! 
from zope.schema import URI

def sanitise_uri(uri):
    '''Sanitise URI
    
    Description
    -----------
    
    Adds the ``http://`` scheme (alias protocol, alias method) to the
    URI if none is provided.'''
    retval = url
    if not(urlparse(uri)[0]):
        retval = 'http://%s' % uri
    return retval

class SaneURI(URI):

    def constraint(self, uri):
        saneUri = sanitise_uri(uri)
        return super(SaneURI, self).constraint(saneUri)
                
    def set(self, instance, uri):
        saneUri = sanitise_uri(uri)
        return super(SaneURI, self).set(instance, saneUri)

