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
        self.users = {}
    
    @property
    def auditItems(self):
        user = self.context
        rawItems = self.queries.get_instance_user_events(
          self.userInfo.id)
        
        events = []
        for i in rawItems:
            i = self.marshal_data(i)
            event = createObject(i['subsystem'], self.context, **i)
            events.append(event)
        return events

    def marshal_data(self, data):
        assert type(data) == dict
        retval = data
        retval.pop('instance_user_id')
        retval['instanceUserInfo'] = self.userInfo

        retval.pop('site_id')
        retval['siteInfo'] = self.siteInfo

        uid = retval.pop('user_id')
        retval['userInfo'] = self.get_userInfo(uid)

        gid = retval.pop('group_id')
        retval['groupInfo'] = self.get_groupInfo(gid)
        
        assert type(retval) == dict
        return retval

    def get_userInfo(self, uid):
        # Cache, as we deal with so many user-infos.
        retval = self.users.get(uid,\
          createObject('groupserver.UserFromId', self.context, uid))
        self.users[uid] = retval
        return retval

    def get_groupInfo(self, gid):
        # TODO: Cache
        return gid and \
          createObject('groupserver.GroupInfo', self.context, gid)\
          or None

