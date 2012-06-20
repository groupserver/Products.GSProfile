# coding=utf-8
from pytz import UTC
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape
from base64 import b64decode
from zope.component import createObject
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, \
  AuditQuery, event_id_from_data
from Products.XWFCore.XWFUtils import munge_date
from utils import profile_interface

SUBSYSTEM = 'groupserver.ProfileAudit'
import logging
log = logging.getLogger(SUBSYSTEM) #@UndefinedVariable

UNKNOWN         = '0'
SET_PASSWORD    = '1'
CHANGE_PROFILE  = '2'
REGISTER        = '3'
CREATE_USER     = '4'
REQUEST_CONTACT = '5'
class ProfileAuditEventFactory(object):
    implements(IFactory)

    title=u'User Profile Audit-Event Factory'
    description=u'Creates a GroupServer audit event for profiles'

    def __call__(self, context, event_id,  code, date,
        userInfo, instanceUserInfo,  siteInfo,  groupInfo = None,
        instanceDatum='', supplementaryDatum='', subsystem=''):

        if (code == SET_PASSWORD):
            event = SetPasswordEvent(context, event_id, date, 
              userInfo, instanceUserInfo, siteInfo,
              instanceDatum, supplementaryDatum)
        elif (code == CHANGE_PROFILE):
            event = ChangeProfileEvent(context, event_id, date, 
              userInfo, instanceUserInfo, siteInfo,
              instanceDatum, supplementaryDatum)
        elif (code == REGISTER):
            event = RegisterEvent(context, event_id, date, 
              userInfo, instanceUserInfo, siteInfo,
              instanceDatum, supplementaryDatum)
        elif (code == REQUEST_CONTACT):
            event = RequestContactEvent(context, event_id, date,
              userInfo, instanceUserInfo, siteInfo,
              instanceDatum, supplementaryDatum)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date, 
              userInfo, instanceUserInfo, siteInfo, None, 
              instanceDatum, supplementaryDatum, SUBSYSTEM)
        assert event
        return event
    
    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)

class SetPasswordEvent(BasicAuditEvent):
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo, 
        siteInfo, instanceDatum,  supplementaryDatum):
        
        BasicAuditEvent.__init__(self, context, id, 
          SET_PASSWORD, d, userInfo, instanceUserInfo, 
          siteInfo, None,  instanceDatum, supplementaryDatum, 
          SUBSYSTEM)
    
    def __str__(self):
        retval = u'%s (%s) set password on %s (%s)' %\
          (self.instanceUserInfo.name, self.instanceUserInfo.id,
           self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event profile-event-%s' % self.code
        retval = u'<span class="%s">Set password</span>' % cssClass
        if self.instanceUserInfo.id != self.userInfo.id:
            retval = u'%s &#8212; %s' %\
              (retval, userInfo_to_anchor(self.userInfo))
        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
        return retval

class ChangeProfileEvent(BasicAuditEvent):
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo, 
        siteInfo, instanceDatum,  supplementaryDatum):
        
        BasicAuditEvent.__init__(self, context, id, 
          CHANGE_PROFILE, d, userInfo, instanceUserInfo, 
          siteInfo, None,  instanceDatum, supplementaryDatum, 
          SUBSYSTEM)
    
    def __str__(self):
        old, new = self.get_old_new()
        fieldName = self.get_fieldname()
        retval = u'%s (%s) changed profile attribute %s (%s) of '\
          u'%s (%s) from %s to %s on %s (%s)' %\
          (self.userInfo.name, self.userInfo.id, 
           fieldName, self.instanceDatum,
           self.instanceUserInfo.name, self.instanceUserInfo.id,
           old, new, self.siteInfo.name, self.siteInfo.id)
        return retval
        
    def get_old_new(self):
        retval = [b64decode(d).decode('utf-8')
                  for d in self.supplementaryDatum.split(',')]
        assert len(retval) == 2
        return retval

    def get_fieldname(self):
        field = self.instanceDatum
        interface = profile_interface(self.context)
        fieldName = interface.get(field, '')
        fieldName = fieldName and fieldName.title
        return fieldName
        
    @property
    def xhtml(self):
        cssClass = u'audit-event profile-event-%s' % self.code
        old, new = self.get_old_new()
        retval = u'<span class="%s">Profile-field '\
          u'<span class="field-%s">%s</span> '\
          u'changed to '\
          u'<code class="new">%s</code> (was '\
          u'<code class="old">%s</code>)</span>' % \
          (cssClass, self.instanceDatum, self.get_fieldname(),
            xml_escape(new), xml_escape(old))
        if self.instanceUserInfo.id != self.userInfo.id:
            retval = u'%s &#8212; %s' %\
              (retval, userInfo_to_anchor(self.userInfo))
        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
        return retval

class RegisterEvent(BasicAuditEvent):
    """Registration Event. The "instanceDatum" is the address used
    to create the new user.
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo, 
        siteInfo, instanceDatum,  supplementaryDatum):
        
        BasicAuditEvent.__init__(self, context, id, 
          REGISTER, d, userInfo, instanceUserInfo, 
          siteInfo, None,  instanceDatum, supplementaryDatum, 
          SUBSYSTEM)
    
    def __str__(self):
        retval = u'Registering a new user with address <%s>' %\
          self.instanceDatum
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event profile-event-%s' % self.code
        retval = u'<span class="%s">Signed up, with address '\
          u'<code class="email">%s</code></span>' %\
            (cssClass, self.instanceDatum)
        if ((self.instanceUserInfo.id != self.userInfo.id)
            and not(self.userInfo.anonymous)):
            retval = u'%s &#8212; %s' %\
              (retval, userInfo_to_anchor(self.userInfo))
        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
        return retval

class CreateUserEvent(BasicAuditEvent):
    """Administrator Creating a User Event. 
    
    The "instanceDatum" is the address used to create the new user.
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo, 
        siteInfo, instanceDatum,  supplementaryDatum):
        
        BasicAuditEvent.__init__(self, context, id, 
          REGISTER, d, userInfo, instanceUserInfo, 
          siteInfo, None,  instanceDatum, supplementaryDatum, 
          SUBSYSTEM)
    
    def __str__(self):
        retval = u'Administrator %s (%s) creating a new user with '\
          u'address <%s>' %\
          (self.userInfo.name, self.userInfo.id, self.instanceDatum)
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event profile-event-%s' % self.code
        retval = u'<span class="%s">Created a user, with address '\
          u'<code class="email">%s</code></span>' %\
            (cssClass, self.instanceDatum)
        if ((self.instanceUserInfo.id != self.userInfo.id)
            and not(self.userInfo.anonymous)):
            retval = u'%s &#8212; %s' %\
              (retval, userInfo_to_anchor(self.userInfo))
        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
        return retval

class RequestContactEvent(BasicAuditEvent):
    """ A user requests contact with the user. 
   
         
    """
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo,
        siteInfo, instanceDatum,  supplementaryDatum):

        BasicAuditEvent.__init__(self, context, id,
          REQUEST_CONTACT, d, userInfo, instanceUserInfo,
          siteInfo, None,  instanceDatum, supplementaryDatum,
          SUBSYSTEM)

    def __str__(self):
        raise NotImplementedError

    @property
    def xhtml(self):
        raise NotImplementedError


class ProfileAuditer(object):
    def __init__(self, user):
        self.user = user
        self.userInfo = createObject('groupserver.LoggedInUser',user)
        self.instanceUserInfo = IGSUserInfo(user)
        self.siteInfo = createObject('groupserver.SiteInfo', user)
        
        self.queries = AuditQuery()
      
        self.factory = ProfileAuditEventFactory()
        
    def info(self, code, instanceDatum = '', supplementaryDatum = ''):
        d = datetime.now(UTC)
        eventId = event_id_from_data(self.userInfo, 
          self.instanceUserInfo, self.siteInfo, code, instanceDatum,
          supplementaryDatum)
          
        e =  self.factory(self.user, eventId,  code, d,
          self.userInfo, self.instanceUserInfo, self.siteInfo, None,
          instanceDatum, supplementaryDatum, SUBSYSTEM)
          
        self.queries.store(e)
        log.info(e)

