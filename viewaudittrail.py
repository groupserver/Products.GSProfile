# coding=utf-8
from Products.Five import BrowserView
from zope.component import createObject, getUtility
from zope.component.interfaces import IFactory
from Products.GSAuditTrail import AuditQuery, IAuditEvent
from Products.CustomUserFolder.interfaces import IGSUserInfo

class GSAuditTrailView(BrowserView):
    '''View the audit-trail for a user'''
    def __init__(self, context, request):
        assert context
        assert request
        BrowserView.__init__(self, context, request)

        self.siteInfo = createObject('groupserver.SiteInfo', 
          context)
        self.userInfo = IGSUserInfo(context)

        da = context.zsqlalchemy
        self.queries = AuditQuery(da)
    
    @property
    def auditItems(self):
        user = self.context
        rawItems = self.queries.get_user_events_on_site(\
          self.userInfo.id, self.siteInfo.id)
        
        events = []
        factories = {}
        users = {}
        for i in rawItems:
            i.pop('instance_user_id')
            i['instanceUserInfo'] = self.userInfo

            i.pop('site_id')
            i['siteInfo'] = self.siteInfo

            uid = i.pop('user_id')
            i['userInfo'] = users.get(uid,\
              createObject('groupserver.UserFromId', self.context, uid))

            gid = i.pop('group_id')
            i['groupInfo'] = gid and \
              createObject('groupserver.GroupInfo', self.context, gid)\
              or None
            
            ssys = i['subsystem']
            f = factories.get(ssys,
                  getUtility(IFactory, ssys, self.context))
            factories[ssys] = f
            event = f(self.context, **i)
            events.append(event)
        return events

