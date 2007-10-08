# coding=utf-8
##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test the Request Password Reset Schema

$Id: test_size.py 61072 2005-10-31 17:43:51Z philikon $
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_posting():
    """
    Test the Request Password Reset Schema

    Set up:
      >>> from zope.app.testing.placelesssetup import setUp, tearDown
      >>> setUp()
      >>> import Products.Five
      >>> import zope.interface, zope.schema
      >>> from zope.interface.verify import verifyObject

      >>> import Products.GSProfile
      >>> from Products.Five import zcml
      >>> zcml.load_config('meta.zcml', Products.Five)
      >>> zcml.load_config('permissions.zcml', Products.Five)
      >>> zcml.load_config('configure.zcml', Products.GSProfile)

      >>> from Products.GSProfile.interfaces import *

    Create an implementation of the IGSRequestPasswordReset schema
      >>> class RequestPasswordReset(object):
      ...     zope.interface.implements(IGSRequestPasswordReset)
      ...     
      ...     email = None
      ...     
      ...     def __init__(self, email):
      ...         self.email = email
      >>> IGSRequestPasswordReset.implementedBy(RequestPasswordReset)
      True
      >>> IGSEmailAddressEntry.implementedBy(RequestPasswordReset)
      True

    Create a test request, which will validate
      >>> okRequest1 = RequestPasswordReset(u'mpj17@onlinegroups.net')
      
    Validate the request
      >>> IGSRequestPasswordReset.providedBy(okRequest1)
      True
      >>> be = IGSRequestPasswordReset.get('email').bind(okRequest1)
      >>> be.validate(be.get(okRequest1))

    Create a test request, which will validate even though the address
    does not exist
      >>> okRequest2 = RequestPasswordReset(u'foo@wibble.bar')
      
    Validate the request
      >>> IGSRequestPasswordReset.providedBy(okRequest2)
      True
      >>> be = IGSRequestPasswordReset.get('email').bind(okRequest2)
      >>> be.validate(be.get(okRequest2))

    Create a test request, which is invalid because the address is 
    incorrect
      >>> badRequest1 = RequestPasswordReset(u'foo@bar')
      
    Validate the request
      >>> IGSRequestPasswordReset.providedBy(badRequest1)
      True
      >>> be = IGSRequestPasswordReset.get('email').bind(badRequest1)
      >>> be.validate(be.get(badRequest1))
      Traceback (most recent call last):
      ...
      ConstraintNotSatisfied: foo@bar

    Create a test request, which is invalid because the address is not
    set
      >>> badRequest2 = RequestPasswordReset(None)
      
    Validate the request
      >>> IGSRequestPasswordReset.providedBy(badRequest2)
      True
      >>> be = IGSRequestPasswordReset.get('email').bind(badRequest2)
      >>> be.validate(be.get(badRequest2))
      Traceback (most recent call last):
      ...
      RequiredMissing
      
    Create a test request, which is invalid because the address contains
    an illegal character
      >>> badRequest3 = RequestPasswordReset(u'foo#blarg@wibble.bar')
      
    Validate the request
      >>> IGSRequestPasswordReset.providedBy(badRequest3)
      True
      >>> be = IGSRequestPasswordReset.get('email').bind(badRequest3)
      >>> be.validate(be.get(badRequest3))
      Traceback (most recent call last):
      ...
      ConstraintNotSatisfied: foo#blarg@wibble.bar
    
    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()

