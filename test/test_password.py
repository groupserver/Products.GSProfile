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
"""Test the Password Schema

$Id: test_size.py 61072 2005-10-31 17:43:51Z philikon $
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_posting():
    """
    Test the Set Password schema

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

      >>> from Products.GSProfile.interfaces import IGSSetPassword

    Create an implementation of the IGSSetPassword schema
      >>> class Password(object):
      ...     zope.interface.implements(IGSSetPassword)
      ...     
      ...     password1 = None
      ...     password2 = None
      ...     
      ...     def __init__(self, first, second):
      ...         self.password1 = first
      ...         self.password2 = second
      >>> IGSSetPassword.implementedBy(Password)
      True

    Create a test password, which will validate
      >>> okPassword = Password(u'foobar', u'foobar')
      
    Validate the ok password
      >>> IGSSetPassword.providedBy(okPassword)
      True
      >>> bp1 = IGSSetPassword.get('password1').bind(okPassword)
      >>> bp1.validate(bp1.get(okPassword))
      >>> bp2 = IGSSetPassword.get('password2').bind(okPassword)
      >>> bp2.validate(bp2.get(okPassword))
      >>> IGSSetPassword.validateInvariants(okPassword)
      
    Create a test password, which is invalid because the two passwords do
    not match
      >>> badPassword1 = Password(u'foobar', u'foboar')
      
    Validate the bad password
      >>> IGSSetPassword.providedBy(badPassword1)
      True
      >>> bp1 = IGSSetPassword.get('password1').bind(badPassword1)
      >>> bp1.validate(bp1.get(badPassword1))
      >>> bp2 = IGSSetPassword.get('password2').bind(badPassword1)
      >>> bp2.validate(bp2.get(badPassword1))
      >>> IGSSetPassword.validateInvariants(badPassword1)
      Traceback (most recent call last):
      ...
      Invalid: Passwords do not match
      
    Create a test password, which is invalid because the two passwords are
    too short
      >>> badPassword2 = Password(u'foo', u'foo')

    Validate the bad password
      >>> IGSSetPassword.providedBy(badPassword2)
      True
      >>> bp1 = IGSSetPassword.get('password1').bind(badPassword2)
      >>> bp1.validate(bp1.get(badPassword2))
      Traceback (most recent call last):
      ...
      TooShort: (u'foo', 4)
      >>> bp2 = IGSSetPassword.get('password2').bind(badPassword2)
      >>> bp2.validate(bp2.get(badPassword2))
      Traceback (most recent call last):
      ...
      TooShort: (u'foo', 4)
      >>> IGSSetPassword.validateInvariants(badPassword2)
            
    Create a test password, which is invalid because one password is too
    short, and the two passwords do not match
      >>> badPassword3 = Password(u'foobar', u'foo')

    Validate the bad password
      >>> IGSSetPassword.providedBy(badPassword3)
      True
      >>> bp1 = IGSSetPassword.get('password1').bind(badPassword3)
      >>> bp1.validate(bp1.get(badPassword3))
      >>> bp2 = IGSSetPassword.get('password2').bind(badPassword3)
      >>> bp2.validate(bp2.get(badPassword3))
      Traceback (most recent call last):
      ...
      TooShort: (u'foo', 4)
      >>> IGSSetPassword.validateInvariants(badPassword3)
      Traceback (most recent call last):
      ...
      Invalid: Passwords do not match

    Create a test password, which is invalid because the first password is
    not set
      >>> badPassword4 = Password(u'foobar', None)
      
    Validate the bad password
      >>> IGSSetPassword.providedBy(badPassword4)
      True
      >>> bp1 = IGSSetPassword.get('password1').bind(badPassword4)
      >>> bp1.validate(bp1.get(badPassword4))
      >>> bp2 = IGSSetPassword.get('password2').bind(badPassword4)
      >>> bp2.validate(bp2.get(badPassword4))
      Traceback (most recent call last):
      ...
      RequiredMissing
      >>> IGSSetPassword.validateInvariants(badPassword4)
      Traceback (most recent call last):
      ...
      Invalid: Passwords do not match

    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()

