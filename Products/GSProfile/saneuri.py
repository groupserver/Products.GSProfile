# coding=utf-8
'''
========================
A Sane URI Schema Field
=======================

The sane URI schema field is like the standard Zope URI field, but it is
far more tolerant of poor input. It is not unheard of for users of a
system to enter domains such as ``groupserver.org`` as a URI, rather 
than strict URIs such as <http://groupserver.org>.

How dear the users fail to follow `RFC2396 
<http://www.ietf.org/rfc/rfc2396.txt>`_ to the letter!'

TODO: Split this off into its own module, so it can be used widely.'''
from urlparse import urlparse # Use urlparse to parse urls. Shock! 
from zope.schema import URI

def sanitise_uri(uri):
    '''Sanitise URI
    
    Description
    -----------
    
    Adds the ``http://`` scheme (alias protocol, alias method) to the
    URI if none is provided.
    
    Arguments
    ---------
    
    ``uri`` The string containing the URI to be sanitised.
    
    Returns
    -------
    
    A string containing the sanitised URI.
    
    Side Effects
    ------------
    
    None.'''
    if uri == None:
      retval = ''
    else:
      retval = uri
      if not(urlparse(uri)[0]):
          retval = 'http://%s' % uri
    return retval

class SaneURI(URI):
    '''Sane URI schema field
    
    Description
    -----------
    
    An extension of the URI schema field that sanitises the input before
    checking it.'''
    def constraint(self, uri):
        saneUri = sanitise_uri(uri)
        return super(SaneURI, self).constraint(saneUri)
    
    def validate(self, uri):
        saneUri = sanitise_uri(uri)
        return super(SaneURI, self).validate(saneUri)
        
    def set(self, instance, uri):
        saneUri = sanitise_uri(uri)
        return super(SaneURI, self).set(instance, saneUri)

