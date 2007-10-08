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

    Create an implementation of the core profile
      >>> class CoreProfile(object):
      ...     zope.interface.implements(IGSCoreProfile)
      ...     
      ...     displayName = None
      ...     nickname = None
      ...     timezone = None
      ...     biography = None
      ...     
      ...     def __init__(self, displayName, nickname, timezone, biography):
      ...         self.displayName = displayName
      ...         self.nickname = nickname
      ...         self.timezone = timezone
      ...         self.biography = biography
      >>> IGSCoreProfile.implementedBy(CoreProfile)
      True

    Create a test profile, which will validate
      >>> okProfile = CoreProfile(u'Michael JasonSmith', 'mpj17', 
      ...   'Pacific/Auckland', u'I am a geek.')

    Validate the request
      >>> IGSCoreProfile.providedBy(okProfile)
      True
      >>> bd = IGSCoreProfile.get('displayName').bind(okProfile)
      >>> bd.validate(bd.get(okProfile))

      >>> bn = IGSCoreProfile.get('nickname').bind(okProfile)
      >>> bn.validate(bn.get(okProfile))

      >>> bt = IGSCoreProfile.get('timezone').bind(okProfile)
      >>> bt.validate(bt.get(okProfile))

      >>> bb = IGSCoreProfile.get('biography').bind(okProfile)
      >>> bb.validate(bb.get(okProfile))

    Create an invalid profile, with broken nickname, and timezone
      >>> badProfile1 = CoreProfile(u' ', ':#//@', 
      ...   'Vogosphere', u'I am a geek.')

    Validate the request
      >>> IGSCoreProfile.providedBy(badProfile1)
      True
      >>> bd = IGSCoreProfile.get('displayName').bind(badProfile1)
      >>> bd.validate(bd.get(badProfile1))
      Traceback (most recent call last):
      ...
      ConstraintNotSatisfied:
      
      >>> bn = IGSCoreProfile.get('nickname').bind(badProfile1)
      >>> bn.validate(bn.get(badProfile1))
      Traceback (most recent call last):
      ...
      InvalidDottedName: :#//@

      >>> bt = IGSCoreProfile.get('timezone').bind(badProfile1)
      >>> bt.validate(bt.get(badProfile1))
      Traceback (most recent call last):
      ...
      ConstraintNotSatisfied: Vogosphere

      >>> bb = IGSCoreProfile.get('biography').bind(badProfile1)
      >>> bb.validate(bb.get(badProfile1))

    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()

