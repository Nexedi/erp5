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

from ZODB.DemoStorage import DemoStorage
from ZODB.ConflictResolution import tryToResolveConflict, ResolvedSerial

try:
    loadEx = DemoStorage.loadEx

except AttributeError: # Zope 2.12
    ##
    # Implement conflict resolution for DemoStorage
    #
    import ZODB.POSException

    def store(self, oid, serial, data, version, transaction):
        assert version=='', "versions aren't supported"
        if transaction is not self._transaction:
            raise ZODB.POSException.StorageTransactionError(self, transaction)

        # Since the OID is being used, we don't have to keep up with it any
        # more. Save it now so we can forget it later. :)
        self._stored_oids.add(oid)

        # See if we already have changes for this oid
        try:
            old = self.changes.load(oid, '')[1]
        except ZODB.POSException.POSKeyError:
            try:
                old = self.base.load(oid, '')[1]
            except ZODB.POSException.POSKeyError:
                old = serial
                
        if old != serial:
            # <patch>
            rdata = tryToResolveConflict(self, oid, old, serial, data)
            if rdata is None:
                raise ZODB.POSException.ConflictError(
                    oid=oid, serials=(old, serial), data=data)
            self.changes.store(oid, old, rdata, '', transaction)
            return ResolvedSerial
            # </patch>

        return self.changes.store(oid, serial, data, '', transaction)

    DemoStorage.store = store

else: # Zope 2.8
    ##
    # Fix bug in DemoStorage.loadEx (it uses 'load' instead of 'loadEx')
    #
    DemoStorage.loadEx = lambda *args: (loadEx(*args) + ('',))[:3]

    ##
    # Implement conflict resolution for DemoStorage
    #
    from ZODB import POSException

    # copied from ZODB/DemoStorage.py and patched
    def store(self, oid, serial, data, version, transaction):
        if transaction is not self._transaction:
            raise POSException.StorageTransactionError(self, transaction)

        self._lock_acquire()
        try:
            old = self._index.get(oid, None)
            if old is None:
                # Hm, nothing here, check the base version:
                if self._base:
                    try:
                        p, tid = self._base.load(oid, '')
                    except KeyError:
                        pass
                    else:
                        old = oid, None, None, p, tid

            nv=None
            if old:
                oid, pre, vdata, p, tid = old

                if vdata:
                    if vdata[0] != version:
                        raise POSException.VersionLockError, oid

                    nv=vdata[1]
                else:
                    nv=old

                if serial != tid:
                  # <patch>
                  rdata = tryToResolveConflict(self, oid, tid, serial, data)
                  if rdata is None:
                    raise POSException.ConflictError(
                        oid=oid, serials=(tid, serial), data=data)
                  data = rdata
                  # </patch>

            r = [oid, old, version and (version, nv) or None, data, self._tid]
            self._tindex.append(r)

            s=self._tsize
            s=s+72+(data and (16+len(data)) or 4)
            if version: s=s+32+len(version)

            if self._quota is not None and s > self._quota:
                raise POSException.StorageError, (
                    '''<b>Quota Exceeded</b><br>
                    The maximum quota for this demonstration storage
                    has been exceeded.<br>Have a nice day.''')

        finally: self._lock_release()
        # <patch>
        if old and serial != tid:
            return ResolvedSerial
        # </patch>
        return self._tid

    DemoStorage.store = store

    def loadSerial(self, oid, serial):
        # XXX should I use self._lock_acquire and self._lock_release ?
        pre = self._index.get(oid)
        while pre:
            oid, pre, vdata, p, tid = pre
            if tid == serial:
                return p
        return self._base.loadSerial(oid, serial)

    DemoStorage.loadSerial = loadSerial

    def loadBefore(self, oid, tid):
        # XXX should I use self._lock_acquire and self._lock_release ?
        end_time = None
        pre = self._index.get(oid)
        while pre:
            oid, pre, vdata, p, start_time = pre
            if start_time < tid:
                return p, start_time, end_time
            end_time = start_time
        base = self._base.loadBefore(oid, tid)
        if base:
            p, start_time, base_end_time = base
            return p, start_time, base_end_time or end_time

    DemoStorage.loadBefore = loadBefore

    def history(self, oid, version=None, length=1, filter=None):
        assert not version
        self._lock_acquire()
        try:
            r = []
            pre = self._index.get(oid)
            while length and pre:
                oid, pre, vdata, p, tid = pre
                assert vdata is None
                d = {'tid': tid, 'size': len(p), 'version': ''}
                if filter is None or filter(d):
                    r.append(d)
                    length -= 1
            if length:
                r += self._base.history(oid, version, length, filter)
            return r
        finally:
            self._lock_release()

    DemoStorage.history = history
