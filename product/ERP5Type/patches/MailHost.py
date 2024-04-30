##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# Copyright (c) 2011 Nexedi SARL and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""
Change default behaviour of MailHost to send mails immediately.
In ERP5, we have Activity Tool to postpone mail delivery.
"""

from inspect import isfunction
import six
if six.PY3:
  from inspect import getfullargspec
else:
  from inspect import getargspec as getfullargspec
from Products.MailHost.MailHost import MailBase


for f in six.itervalues(MailBase.__dict__):
  if isfunction(f):
    argspec = getfullargspec(f)
    args = argspec.args
    defaults = argspec.defaults
    try:
      i = args.index('immediate') - len(args)
    except ValueError:
      continue
    f.__defaults__ = defaults[:i] + (True,) + defaults[i+1 or len(args):]

from App.special_dtml import DTMLFile
MailBase.manage = MailBase.manage_main = DTMLFile('dtml/manageMailHost', globals())
MailBase.smtp_socket_timeout = 16.

from functools import partial
MailBase__makeMailer = MailBase._makeMailer
def _makeMailer(self):
  """ Create a SMTPMailer """
  smtp_mailer = MailBase__makeMailer(self)
  smtp_mailer.smtp = partial(smtp_mailer.smtp, timeout=self.smtp_socket_timeout)
  return smtp_mailer

MailBase._makeMailer = _makeMailer
