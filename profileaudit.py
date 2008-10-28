# coding=utf-8
from datetime import date
import md5
from zope.component import createObject
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.XWFCore.XWFUtils import convert_int2b62
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, \
  AuditQuery

SUBSYSTEM = 'groupserver.ProfileAudit'
import logging
log = logging.getLogger(SUBSYSTEM) #@UndefinedVariable

UNKNOWN        = 0
SET_PASSWORD   = 1
CHANGE_PROFILE = 2

class ProfileAuditEventFactory(object):
    implements(IFactory)

    title=u'User Profile Audit-Event Factory'
    description=u'Creates a GroupServer audit event for profiles'

    def __call__(self, context, eventId,  code, d,
        userInfo, instanceUserInfo,  siteInfo,  
        instanceDatum, supplementaryDatum):

        if code == SET_PASSWORD:
            event = SetPasswordEvent(context, eventId, d, 
              userInfo, instanceUserInfo, siteInfo,
              instanceDatum, supplementaryDatum)
        else:
            event = BasicAuditEvent(context, eventId, UNKNOWN, d, 
              userInfo, instanceUserInfo, siteInfo, None, 
              instanceDatum, supplementaryDatum, SUBSYSTEM)
        print event
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
        cssClass = u'audit-event profile-event-%s' % self.eventCode
        retval = u'<span class="%s">%s set password</span>' % \
          (cssClass, 
           userInfo_to_anchor(self.instanceUserInfo),
           self.instanceDatum)
        return retval

class ProfileAuditer(object):
    def __init__(self, user):
        self.user = user
        self.userInfo = createObject('groupserver.LoggedInUser',user)
        self.instanceUserInfo = IGSUserInfo(user)
        self.siteInfo = createObject('groupserver.SiteInfo', user)
        
        da = user.zsqlalchemy
        self.queries = AuditQuery(da)
      
        self.factory = ProfileAuditEventFactory()
        
    def info(self, code, instanceDatum = '', supplementaryDatum = ''):
        d = date.today()
        
        e = '%s-%s %s-%s %s-%s %s %s %s %s' % \
          (self.userInfo.name, self.userInfo.id,
           self.instanceUserInfo.name, self.instanceUserInfo.id,
           self.siteInfo.name, self.siteInfo.id,
           d, code, instanceDatum, supplementaryDatum)
        eNum = long(md5.new(e).hexdigest(), 16)
        eventId = str(convert_int2b62(eNum))
        
        e = self.factory(self.user, eventId,  code, d,
          self.userInfo, self.instanceUserInfo, self.siteInfo,
          instanceDatum, supplementaryDatum)
        self.queries.store(e)
        log.info(e)

