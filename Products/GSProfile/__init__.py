# coding=utf-8
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class

utils_security = ModuleSecurityInfo('Products.GSProfile.utils')
utils_security.declarePublic('send_verification_message')
utils_security.declarePublic('send_add_user_notification')

from utils import create_user_from_email
utils_security = ModuleSecurityInfo('Products.GSProfile.utils')
utils_security.declarePublic('create_user_from_email')

