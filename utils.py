#coding: utf-8
import time, md5
from zope.component import createObject
from zope.schema import *
from zope.interface import implements, providedBy, implementedBy,\
  directlyProvidedBy, alsoProvides

from Products.XWFCore import XWFUtils
from Products.CustomUserFolder.CustomUser import CustomUser

import logging
log = logging.getLogger('GSProfile Utilities')

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

def login(context, user):
    assert context
    assert user
    site_root = context.site_root()
    site_root.cookie_authentication.credentialsChanged(user,
      user.getId(), user.get_password())
    m = 'utils.login: Logged in the user %s (%s)' % \
      (user.getProperty('fn', ''), user.getId())
    log.info(m)

def verificationId_from_email(email):
      # Let us hope that the verification ID *is* unique
      vNum = long(md5.new(time.asctime() + email).hexdigest(), 16)
      verificationId = str(XWFUtils.convert_int2b62(vNum))
      assert type(verificationId) == str
      return verificationId

def address_exists(context, emailAddress):
    acl_users = __get_acl_users_for_context(context)
    user = acl_users.get_userIdByEmail(emailAddress)
    retval = user != None
    
    assert type(retval) == bool
    return retval
      
def send_verification_message(context, user, email):
    '''Send a email-address verification message to a user
    
    ARGUMENTS
      context: The context for the operation
      user:    The user who is reciving the email message
      email:   The email address to verify
      
    RETURNS
      None
      
    SIDE EFFECTS
      Adds an entry to the email-address-verification table.
    '''
    assert context != None
    assert user!= None
    assert email in user.get_emailAddresses(), \
      'Email <%s> not in %s' % (email, user.get_emailAddresses())
    siteInfo = createObject('groupserver.SiteInfo', context)

    verificationId = verificationId_from_email(email)
    user.add_emailAddressVerification(verificationId, email)
    
    n_dict = {}
    n_dict['verificationId'] = verificationId
    n_dict['userId'] = user.getId()
    n_dict['userFn'] = user.getProperty('fn','')
    n_dict['siteName'] = siteInfo.get_name()
    n_dict['siteURL'] = siteInfo.get_url()
    user.send_notification(
      n_type='verify_email_address', 
      n_id='default',
      n_dict=n_dict, 
      email_only=[email])
    m = 'utils.send_verification_message: Sent an email-verification '\
      'message to <%s> for the user %s (%s)' % \
        (email, user.getProperty('fn', ''), user.getId())
    log.info(m)

def create_user_from_email(context, email):
    assert email
    assert type(email) == str
    assert '@' in email
    m = 'utils.create_user_from_email: Creating a new user for the '\
      'address <%s>' % email
    log.info(m)
    
    userNum = long(md5.new(time.asctime() + email).hexdigest(), 16)
    userId = str(XWFUtils.convert_int2b62(userNum))

    # Ensure that the user ID is unique. There is also has a race 
    #   condition, and the loop is non-deterministic.
    acl_users = __get_acl_users_for_context(context)
    while (acl_users.getUserById(userId)):
        userNum = long(md5.new(time.asctime() + email).hexdigest(), 16)
        userId = str(XWFUtils.convert_int2b62(userNum))
        
    displayName = email.split('@')[0]
    
    user = acl_users.simple_register_user(email, userId, displayName)
    m = 'utils.create_user_from_email: Created a new user %s (%s)' % \
      (user.getProperty('fn', ''), user.getId())
    log.info(m)
    
    assert user
    assert isinstance(user, CustomUser)
    return user

def send_add_user_notification(user, admin, groupInfo, message=u''):
    """Send an Add User notification to a new user
    
    DESCRIPTION
      When a new user is added to the site, he or she needs to be informed
      of their new account. This function sends the appropriate 
      notification to the user.
      
    ARGUMENTS
      user        The instance of the user to add.
      admin       The instance of the administrator who is adding the user.
      groupInfo   Information about the group the user is being added to.
      message     An optional message to send to the user, in addition to
                  the standard message.
    RETURNS
      None.
      
    SIDE EFFECTS
      * Creates a verification-ID for the user's first (and only) email
        address and adds it to the email-address verification table.
      * Sends an "admin_create_new_user" message to the user, containing
        "message".
    """
    assert user
    assert isinstance(user, CustomUser)
    assert admin
    #assert isinstance(admin, CustomUser)
    assert groupInfo
    assert (type(message) in (str, unicode)) or (message == None)
    
    siteInfo = groupInfo.siteInfo
    # As the user is a brand-new user, he or she only has one address.
    email = user.get_emailAddresses()[0]
    invitationId = verificationId_from_email(email)

    user.add_invitation(invitationId, admin.getId(),
      siteInfo.get_id(), groupInfo.get_id())
    user.add_emailAddressVerification(invitationId, email)
    
    if message == None:
        message = ''
    
    n_dict = {}
    n_dict['verificationId'] = invitationId
    n_dict['userId'] = user.getId()
    n_dict['userFn'] = user.getProperty('fn','')
    n_dict['siteName'] = siteInfo.get_name()
    n_dict['groupName'] = groupInfo.get_name()
    n_dict['siteURL'] = siteInfo.get_url()
    n_dict['admin'] = {
      'name':    admin.getProperty('fn', ''),
      'address': admin.get_preferredEmailAddresses()[0],
      'message': message}
    
    user.send_notification(
      n_type='admin_create_new_user', 
      n_id='default',
      n_dict=n_dict, 
      email_only=[email])

def join_group(user, groupInfo):
    assert user
    assert isinstance(user, CustomUser)
    assert groupInfo
    assert groupInfo.siteInfo
    
    siteInfo = groupInfo.siteInfo

    fn = user.getProperty('fn', '')
    uid = user.getId()
    m = u'utils.join_group: adding the user %s (%s) to the group %s (%s) '\
        u'on %s (%s)' % \
        (fn,                   uid, 
         groupInfo.get_name(), groupInfo.get_id(),
         siteInfo.get_name(), siteInfo.get_id())
    log.info(m)

    userGroups = user.getGroups()
    userGroup = '%s_member' % groupInfo.get_id()
    assert userGroup not in userGroups, 'User %s (%s) already in %s' % \
      (fn, uid, userGroup)
    user.add_groupWithNotification(userGroup)

    siteGroup = '%s_member' % siteInfo.get_id()
    if siteGroup not in userGroups:
        m = u'AdminJoinEditProfileForm: the user %s (%s) is not a '\
            u' member of the site %s (%s)' % \
              (fn, uid, siteInfo.get_name(), siteInfo.get_id())
        log.info(m)
        user.add_groupWithNotification(siteGroup)

    userGroupsAssert = user.getGroups()
    assert userGroup in userGroupsAssert
    assert siteGroup in userGroupsAssert


def enforce_schema(inputData, schema):
    """
    SIDE EFFECTS
      * "inputData" is stated to provide the "schema" interface
      * "inputData" will provide all the properties defined in "schema"
    """

    typeMap = {
      Text:      'ulines',
      TextLine:  'ustring',
      ASCII:     'lines',
      ASCIILine: 'string',
      URI:       'string',
      Bool:      'bool',
      Float:     'float',
      Int:       'int',
      Datetime:  'date',
      Date:      'date',
    }
    fields = [field[0] for field in getFieldsInOrder(schema)]
    for field in fields:
        if not hasattr(inputData, field):
            default = schema.get(field).default or ''
            t = typeMap.get(type(schema.get(field)), 'ustring')
            inputData.manage_addProperty(field, default, t)
    alsoProvides(inputData, schema)

