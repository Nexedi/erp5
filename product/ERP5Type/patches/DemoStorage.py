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

if 1:
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
