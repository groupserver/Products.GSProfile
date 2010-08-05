# coding=utf-8
''' Implementation of the Edit Image form.
'''
try:
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm

from Products.XWFCore import XWFUtils
from zope.component import createObject
from zope.interface import alsoProvides
from zope.formlib import form
from zope.schema import getFieldsInOrder

from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from interfaceCoreProfile import IGSProfileImage
from Products.CustomUserFolder.interfaces import IGSUserInfo

import os

class GSEditImageForm(PageForm):
    label = u'Change Image'
    pageTemplateFileName = 'browser/templates/edit_image.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSProfileImage, render_context=True)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.siteInfo = createObject('groupserver.SiteInfo', context)
        context.image = None
        self.userInfo = IGSUserInfo(context)
        
        if not(hasattr(context, 'showImage')):
            context.manage_addProperty('showImage', True, 'boolean')
        alsoProvides(context, IGSProfileImage)

    @property
    def userName(self):
        retval = XWFUtils.get_user_realnames(self.context)
        return retval

    @property
    def userImageUrl(self):
        retval = self.context.get_image() or ''
        assert type(retval) == str
        return retval

    # --=mpj17=--
    # The "form.action" decorator creates an action instance, with
    #   "handle_reset" set to the success handler,
    #   "handle_reset_action_failure" as the failure handler, and adds the
    #   action to the "actions" instance variable (creating it if 
    #   necessary). I did not need to explicitly state that "Edit" is the 
    #   label, but it helps with readability.
    @form.action(label=u'Change', failure='handle_set_action_failure')
    def handle_reset(self, action, data):
        # This may seem a bit daft, but there is method to my madness. The
        #   "showImage" value is set by simple assignment, while the
        #   "image" is set using 
        assert self.context
        assert self.form_fields
        
        alteredFields = [datum[0] 
                         for datum in getFieldsInOrder(IGSProfileImage)
                         if data[datum[0]] != getattr(self.context, datum[0])]

        if 'showImage' in alteredFields:
            self.context.showImage = data['showImage']
        if 'image' in alteredFields:
            self.set_image(data['image'])
            
        if alteredFields:
            fields = [IGSProfileImage.get(name).title
                      for name in alteredFields]
            f = ' and '.join([i for i in (', '.join(fields[:-1]), fields[-1])
                              if i])
            self.status = u'Changed %s' % f
        else:
            self.status = u"No fields changed."
        assert self.status
        assert type(self.status) == unicode

    def handle_set_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

    def set_image(self, image):
        siteId = self.context.site_root().getId()
        contactImageDir = XWFUtils.locateDataDirectory("groupserver.user.image",
                                                       (siteId,))

        userImageName = '%s.jpg' % self.context.getId()
        
        userImagePath = os.path.join(contactImageDir, userImageName)
        
        f = file(userImagePath, 'wb')
        f.write(str(image))
        f.close()
