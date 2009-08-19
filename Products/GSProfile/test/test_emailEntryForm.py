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
      >>> from Products.GSProfile.request_password_reset import RequestPasswordResetForm
      >>> len(RequestPasswordResetForm.form_fields)
      1
      
    Load GroupServer Content
      >>> import Products.GSContent
      >>> zcml.load_config('configure.zcml', Products.GSContent)
      
    Create some context
      >>> from Products.Five.tests.testing.simplecontent import manage_addSimpleContent
      >>> manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
      >>> uf = self.folder.acl_users
      >>> uf._doAddUser('manager', 'r00t', ['Manager'], [])
      >>> self.login('manager')

    Create a request
      >>> from zope.publisher.browser import TestRequest
      >>> request = TestRequest()
      >>> request.RESPONSE = request.response

    Test the form
      >>> testPage = RequestPasswordResetForm(self.folder, request)
      >>> testPage = testPage.__of__(self.folder.testoid) 
      >>> testPage.update()
      >>> widgets = [w for w in testPage.widgets]
      >>> len(widgets)
      1
      >>> widgets[0].label
      u'Email Address'
      >>> widgets[0].name
      'form.email'
      >>> len(testPage.availableActions())
      1
      >>> testPage.availableActions()[0].label
      u'Reset'      
      >>> print testPage() # doctest: +NORMALIZE_WHITESPACE
      <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
      ...
      <title>
          Reset Password
      </title>
      ...
      <label for="form.email"
         title="Your email address.">* Email Address</label>
      ...
      <input class="textType" id="form.email" name="form.email" size="20" 
      type="text" value=""  />
      ...
      <input type="submit" id="form.actions.reset" 
        name="form.actions.reset" value="Reset" class="button" />
      ...

    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()

