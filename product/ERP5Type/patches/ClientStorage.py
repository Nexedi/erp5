##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# This is a backport of http://svn.zope.org/?rev=106514&view=rev for Zope 2.8.

try:
    from ThreadedAsync import LoopCallback

except ImportError:
    pass # nothing to do for recent Zope

else:
    # Switch Zope 2.8 to async I/O for ZEO client storages

    import Lifetime
    Lifetime_lifetime_loop = Lifetime.lifetime_loop

    def lifetime_loop():
        from asyncore import socket_map as map
        LoopCallback._loop_lock.acquire()
        try:
            LoopCallback._looping = map
            while LoopCallback._loop_callbacks:
                cb, args, kw = LoopCallback._loop_callbacks.pop()
                cb(map, *args, **(kw or {}))
        finally:
            LoopCallback._loop_lock.release()
        return Lifetime_lifetime_loop()

    Lifetime.lifetime_loop = lifetime_loop

    # Prevent invalidations from being processed out of order

    from ZEO.ClientStorage import ClientStorage

    def tpc_finish(self, txn, f=None):
        """Storage API: finish a transaction."""
        if txn is not self._transaction:
            return
        self._load_lock.acquire()
        try:
            if self._midtxn_disconnect:
                raise ClientDisconnected(
                       'Calling tpc_finish() on a disconnected transaction')

            # The calls to tpc_finish() and _update_cache() should
            # never run currently with another thread, because the
            # tpc_cond condition variable prevents more than one
            # thread from calling tpc_finish() at a time.
            # <patch/>
            self._lock.acquire()  # for atomic processing of invalidations
            try:
                tid = self._server.tpc_finish(id(txn)) # <patch/>
                self._update_cache(tid)
                if f is not None:
                    f(tid)
            finally:
                self._lock.release()

            r = self._check_serials()
            assert r is None or len(r) == 0, "unhandled serialnos: %s" % r
        finally:
            self._load_lock.release()
            self.end_transaction()

    ClientStorage.tpc_finish = tpc_finish

    from ZODB.Connection import Connection

    def invalidate(self, tid, oids):
        """Notify the Connection that transaction 'tid' invalidated oids."""
        self._inv_lock.acquire()
        try:
            if self._txn_time is None:
                self._txn_time = tid
            # <patch>
            elif tid < self._txn_time:
                raise AssertionError("invalidations out of order, %r < %r"
                                     % (tid, self._txn_time))
            # </patch>
            self._invalidated.update(oids)
        finally:
            self._inv_lock.release()

    Connection.invalidate = invalidate
