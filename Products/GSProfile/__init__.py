# coding=utf-8
import profileContextMenu, utils, formwidgets, requiredwidgetsjavascript
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class

from utils import create_user_from_email
utils_security = ModuleSecurityInfo('Products.GSProfile.utils')
utils_security.declarePublic('create_user_from_email')

