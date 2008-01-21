#coding: utf-8
import time, md5
from zope.component import createObject
from Products.XWFCore import XWFUtils
import logging
log = logging.getLogger('GSProfile Utilities')

def login(context, user):
    assert context
    assert user
    site_root = context.site_root()
    site_root.cookie_authentication.credentialsChanged(user,
      user.getId(), user.get_password())          
    m = 'utils.login: Logged in the user "%s"' % user.getId()
    log.info(m)

def verificationId_from_email(email):
      # Let us hope that the verification ID *is* unique
      vNum = long(md5.new(time.asctime() + email).hexdigest(), 16)
      verificationId = str(XWFUtils.convert_int2b62(vNum))
      assert type(verificationId) == str
      return verificationId

def address_exists(context, emailAddress):
    acl_users = context.site_root().acl_users
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
    assert email in user.get_emailAddresses()
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
      'message to <%s> for the user "%s"' % (email, user.getId())
    log.info(m)

