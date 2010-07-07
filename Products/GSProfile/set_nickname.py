# coding=utf-8
'''Implementation of the Edit Image form.
'''
try:
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm    

from zope.component import createObject, adapts
from zope.interface import implements, providedBy, implementedBy,\
  directlyProvidedBy, alsoProvides
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.app.form.browser import MultiCheckBoxWidget, SelectWidget,\
  TextAreaWidget
from zope.security.interfaces import Forbidden
from zope.app.apidoc.interface import getFieldsInOrder
from Products.XWFCore import XWFUtils
from interfaceCoreProfile import *
from Products.CustomUserFolder.interfaces import ICustomUser, IGSUserInfo

class GSSetNickname(PageForm):
    label = u'Set Nickname'
    pageTemplateFileName = 'browser/templates/set_nickname.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSSetNickname, render_context=False)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        self.userInfo = IGSUserInfo(context)

    @property
    def allowSetNickname(self):
        retval = self.userInfo.nickname == self.userInfo.id
        assert type(retval) == bool
        return retval

    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Edit" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Set', failure='handle_set_action_failure')
    def handle_set(self, action, data):
        # This may seem a bit daft, but there is method to my madness. The
        #   "showImage" value is set by simple assignment, while the
        #   "image" is set using 
        assert self.context
        assert self.form_fields
        nickname = data['nickname']
        self.userInfo.user.add_nickname(nickname)
        url = '%s%s' %(self.siteInfo.url, self.userInfo.url)
        self.status = u'The nickname "%s" has been set. Your profile can '\
          u'now be accessed through '\
          u'<a href="%s"><code class="url">%s</code></a>.' %\
          (nickname, url, url)
        assert self.status
        assert type(self.status) == unicode

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def set_image(self, image):
        assert self.context.contactsimages
        images = self.context.contactsimages
        
        userImageName = '%s.jpg' % self.context.getId()
        origimage = getattr(images, userImageName, None)
        if origimage:
            images.manage_delObjects([origimage.getId()])

        userName = XWFUtils.get_user_realnames(self.context)
        images.manage_addImage(userImageName, image, userName)

