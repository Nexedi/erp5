##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from transaction._transaction import Transaction

if not hasattr(Transaction, 'addBeforeCommitHook'):

  def Transaction_addBeforeCommitHook(self, hook, args=(), kws=None):
    if kws is None:
      kws = {}
    self.beforeCommitHook(hook, *args, **kws)

  import logging
  logger = logging.getLogger(__name__)
  logger.info("Patching Transaction with forward compatibility for "
              ".addBeforeCommitHook()")
  Transaction.addBeforeCommitHook = Transaction_addBeforeCommitHook
