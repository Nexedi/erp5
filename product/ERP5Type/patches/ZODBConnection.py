##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import time
from Products.ERP5Type.Timeout import TimeoutReachedError, getDeadline
from ZODB.Connection import Connection

FORCE_STORAGE_SYNC_ON_CONNECTION_OPENING = False

if 1: # for quick disabling.

    if hasattr(Connection, '_storage_sync'): # ZODB<5
        # BBB: For ZEO<5, use a synchronous call to make sure we have received
        #      all invalidation methods that could be stuck in the wire so MVCC
        #      behaves correctly. This can be seen as a "network barrier",
        #      so that, for instance, activity processing can see a recent
        #      enough state of the ZODB.
        #      ZEO5 has an option and NEO does it by default.

        def newTransaction(self, *ignored):
            zeo = getattr(self._storage, '_server', None)
            if zeo is not None:
                zeo.getAuthProtocol()
            self._storage_sync()

        Connection.newTransaction = newTransaction

    if FORCE_STORAGE_SYNC_ON_CONNECTION_OPENING:

        # Whenever an connection is opened (and there's usually an existing one
        # in DB pool that can be reused) whereas the transaction is already
        # started, we must make sure that proper storage setup is done by
        # calling Connection.newTransaction.
        # For example, there's no open transaction when a ZPublisher/Publish
        # transaction begins.

        def open(self, *args, **kw):
            def _flush_invalidations():
                acquire = self._db._a
                try:
                    self._db._r() # this is a RLock
                except RuntimeError:
                    acquire = lambda: None
                try:
                    del self._flush_invalidations
                    self.newTransaction()
                finally:
                    acquire()
                    self._flush_invalidations = _flush_invalidations
            self._flush_invalidations = _flush_invalidations
            try:
                Connection_open(self, *args, **kw)
            finally:
                del self._flush_invalidations

        Connection_open = Connection.open
        Connection.open = open

    setstate_orig = Connection.setstate
    def setstate(self, obj):
        deadline = getDeadline()
        if deadline is not None and deadline < time.time():
          raise TimeoutReachedError
        setstate_orig(self, obj)

    Connection.setstate = setstate
