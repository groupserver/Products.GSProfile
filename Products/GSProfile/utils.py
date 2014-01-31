# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, unicode_literals
from logging import getLogger
log = getLogger('GSProfile Utilities')
from md5 import new as new_md5
from string import ascii_lowercase, digits
from time import asctime
from zope.schema import Text, TextLine, ASCII, ASCIILine, URI, Bool, Float, \
    Int, Datetime, Date, getFieldsInOrder
from zope.interface import alsoProvides
from Products.XWFCore.XWFUtils import convert_int2b62, assign_ownership
from Products.CustomUserFolder.CustomUser import CustomUser
from Products.CustomUserFolder.interfaces import IGSUserInfo
from gs.profile.email.base.emailuser import EmailUser
from . import interfaces
__context_acl_users = {}


def __get_acl_users_for_context(context):
    assert context
    if context not in __context_acl_users:
        acl_users = context.site_root().acl_users
        __context_acl_users[context] = acl_users
    else:
        acl_users = __context_acl_users[context]
    assert acl_users
    return acl_users
get_acl_users_for_context = __get_acl_users_for_context


def login(context, user):
    assert context
    assert user
    site_root = context.site_root()
    site_root.cookie_authentication.credentialsChanged(user,
      user.getId(), user.get_password())
    m = 'utils.login: Logged in the user %s (%s)' % \
      (user.getProperty('fn', ''), user.getId())
    log.info(m)


def create_user_from_email(context, email):
    assert email
    assert type(email) == str, 'Email is a %s, not a str' % type(email)
    assert '@' in email
    m = 'utils.create_user_from_email: Creating a new user for the '\
      'address <%s>' % email
    log.info(m)

    userNum = long(new_md5(asctime() + email).hexdigest(), 16)
    userId = str(convert_int2b62(userNum))

    # Ensure that the user ID is unique. There is also has a race
    #   condition, and the loop is non-deterministic.
    acl_users = __get_acl_users_for_context(context)
    while (acl_users.getUserById(userId)):
        userNum = long(new_md5(asctime() + email).hexdigest(), 16)
        userId = str(convert_int2b62(userNum))

    displayName = email.split('@')[0]

    user = acl_users.simple_register_user(email, userId, displayName)
    userInfo = IGSUserInfo(user)
    emailUser = EmailUser(context, userInfo)
    emailUser.set_delivery(email)

    # --=mpj17=-- Ensure that the user's profile is owned by the user, and
    #   *only* the user.
    assign_ownership(user, user.getId(), recursive=0,
      acl_user_path='/'.join(acl_users.getPhysicalPath()))
    user.manage_delLocalRoles([uid for uid in
                               user.users_with_local_role('Owner')
                               if uid != userId])

    m = 'utils.create_user_from_email: Created a new user %s (%s)' % \
      (user.getProperty('fn', ''), user.getId())
    log.info(m)

    assert user
    assert isinstance(user, CustomUser)
    return user


def enforce_schema(inputData, schema):
    """
    SIDE EFFECTS
      * "inputData" is stated to provide the "schema" interface
      * "inputData" will provide all the properties defined in "schema"
    """

    typeMap = {
      Text: 'text',
      TextLine: 'string',
      ASCII: 'text',
      ASCIILine: 'string',
      URI: 'string',
      Bool: 'boolean',
      Float: 'float',
      Int: 'int',
      Datetime: 'date',
      Date: 'date',
    }
    fields = [field[0] for field in getFieldsInOrder(schema)]
    for field in fields:
        if not hasattr(inputData, field):
            m = u'%s has no attr %s' % (inputData.getId(), field)
            log.debug(m)
            default = schema.get(field).default or ''
            t = typeMap.get(type(schema.get(field)), 'ustring')
            inputData.manage_addProperty(field, default, t)
    alsoProvides(inputData, schema)


ALLOWED_URL_CHARS = ascii_lowercase + digits + "_-.'"


def escape_c(c):
    """Escape Character

    DESCRIPTION
        Escape, into hex, characters that are not allowed in normal
        nicknames. This is not a complete implementation of RFC 3987
        <http://www.ietf.org/rfc/rfc3987.txt>

    ARGUMENTS
        c: A character. It can be a Unicode or ASCII character

    RETURNS
        A string, that may or may not be escaped. If the character is
        escaped, then it will be converted into hexadecimal, with a
        '%x' at the start.

    SIDE EFFECTS
        None.
    """
    retval = ''
    if c in ALLOWED_URL_CHARS:
        retval = str(c)
    else:
        retval = ''.join([hex(ord(d)).replace('0x', r'%')
                          for d in c.encode('UTF-8', 'ignore')])
    assert retval
    assert type(retval) == str
    return retval


def profile_interface(context):
    interfaceName = profile_interface_name(context)

    assert hasattr(interfaces, interfaceName), \
        'Interface "%s" not found.' % interfaceName
    interface = getattr(interfaces, interfaceName)
    return interface


def profile_interface_name(context):
    site_root = context.site_root()
    assert hasattr(site_root, 'GlobalConfiguration')
    config = site_root.GlobalConfiguration

    interfaceName = config.getProperty('profileInterface',
                                        'IGSCoreProfile')
    return interfaceName
