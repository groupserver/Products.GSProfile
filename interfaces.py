"""Interfaces for the registration and password-reset pages."""
import re
from zope.interface.interface import Interface, Invalid, invariant
from zope.schema import *


class IGSSetPassword(Interface):
    """Schema for setting the user's password. The password is entered
      twice by the user, to confirm that it is correct."""
      
    password1 = Password(title=u'Password',
        description=u'Enter your password.',
        required=True,
        min_length=4)
        
    password2 = Password(title=u'Confirm Password',
        description=u'Confirm your password',
        required=True,
        min_length=4)

    @invariant
    def passwordsMatch(passwords):
        if passwords.password1 != passwords.password2:
            raise Invalid('Passwords do not match')


EMAIL_RE = r'[a-zA-Z0-9\._%-]+@([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,4}'
check_email = re.compile(EMAIL_RE).match
class IGSRequestPasswordReset(Interface):
    """Schema used to request that the user's password is reset.
    """

    email = TextLine(title=u'Email Address',
        description=u'The email address that you use for this site',
        required=True,
        constraint=check_email)

