############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# Copyright (c) 2002,2005,2007 Nexedi SA and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################

# Add beforeCommitHook into Transaction under Zope 2.7. This API is compatible
# with Zope 2.8.
try:
    from ZODB.Transaction import Transaction
    
    super__commit = Transaction.commit
    super__init = Transaction.__init__

    def __init__(self, *args, **kw):
      super__init(self, *args, **kw)
      self._before_commit = []

    def commit(self, subtransaction=None):
      """Finalize the transaction."""
      if not subtransaction:
        self._callBeforeCommitHooks()

      return super__commit(self, subtransaction=subtransaction)
   
    def beforeCommitHook(self, hook, *args, **kws):
        self._before_commit.append((hook, args, kws))

    def _callBeforeCommitHooks(self):
        # Call all hooks registered, allowing further registrations
        # during processing.
        while self._before_commit:
            hook, args, kws = self._before_commit.pop(0)
            hook(*args, **kws)

    from new import instancemethod
    Transaction.__init__ = instancemethod(__init__, None, Transaction)
    Transaction.commit = instancemethod(commit, None, Transaction)
    Transaction.beforeCommitHook = instancemethod(beforeCommitHook, None, 
                                                  Transaction)
    Transaction._callBeforeCommitHooks = instancemethod(_callBeforeCommitHooks,
                                                        None, Transaction)
except ImportError:
    # On Zope 2.8, do not patch Transaction.
    pass
