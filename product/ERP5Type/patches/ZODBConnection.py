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

# override ZODB.Connection.newTransaction() to do a synchronous call before
# flushing all invalidations, this will serve as a "network barrier" that
# will force Connection to wait for all invalidations sent from other parallel
# transactions so that, for instance, activity processing can see a recent
# enough state of the ZODB.

from ZODB.Connection import Connection

FORCE_STORAGE_SYNC_ON_CONNECTION_OPENING = False

if 1: # keep indentation. Also good for quick disabling.

    def ping(self):
        # Use a synchronous call to make sure we have received all invalidation
        # methods that could be stuck in the wire so MVCC behaves correctly.
        # XXX Use a proper ping method exported by ClientStorage instead of
        # this hack
        ping = getattr(getattr(self._storage, '_server', None),
                       'getAuthProtocol',
                       lambda: None)
        ping()

    def newTransaction(self, *ignored):
        self.ping()
        self._storage_sync()

    Connection.ping = ping
    Connection.newTransaction = newTransaction

    # See also neo/client/__init__.py from NEOPPOD project
    if FORCE_STORAGE_SYNC_ON_CONNECTION_OPENING:

      try:
        if Connection._nexedi_fix != 4:
            raise Exception("A different ZODB fix is already applied")
      except AttributeError:
        Connection._nexedi_fix = 4

        # Whenever an connection is opened (and there's usually an existing one
        # in DB pool that can be reused) whereas the transaction is already
        # started, we must make sure that proper storage setup is done by
        # calling Connection.newTransaction.
        # For example, there's no open transaction when a ZPublisher/Publish
        # transaction begins.

        import thread

        def open(self, *args, **kw):
            def _flush_invalidations():
                acquire = self._db._a
                try:
                    self._db._r()
                except thread.error:
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
