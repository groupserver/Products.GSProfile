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
      >>> from Products.Five import zcml
      >>> zcml.load_config('meta.zcml', Products.Five)
      >>> zcml.load_config('permissions.zcml', Products.Five)

      >>> import zope.interface, zope.schema
      >>> from zope.interface.verify import verifyObject

      >>> import Products.Five.formlib, Products.Five.form
      >>> zcml.load_config('configure.zcml', Products.Five.formlib)
      >>> zcml.load_config('configure.zcml', Products.Five.form)

      >>> import Products.GSProfile
      >>> zcml.load_config('configure.zcml', Products.GSProfile)
      >>> from Products.GSProfile.interfaces import *

    Create the test form
      >>> from zope.formlib import form
      >>> class TestForm(object):
      ...     form_fields = form.Fields(IGSRequestPasswordReset)
      ... 
      ...     def __init__(self, context, request):
      ...         self.context, self.request = context, request
      ... 
      ...     def __call__(self, ignore_request=False):
      ...         widgets = form.setUpWidgets(self.form_fields, 'form',
      ...           self.context, self.request, 
      ...           ignore_request=ignore_request)
      ...         return u'\\n'.join([w() for w in widgets])
      ...
      >>> len(TestForm.form_fields)
      1
      >>> from zope.publisher.browser import TestRequest
      >>> request = TestRequest()
      >>> print TestForm(None, request)() # doctest: +NORMALIZE_WHITESPACE
      <input class="textType" id="form.email" name="form.email" size="20" type="text" value=""  />
      
    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()

