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

