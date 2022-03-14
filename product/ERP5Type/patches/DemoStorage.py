##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# Copyright (c) 2010-2013 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from ZODB import DemoStorage as _DemoStorage
from ZODB.ConflictResolution import ConflictResolvingStorage
from ZODB.POSException import ConflictError

class DemoStorage(_DemoStorage.DemoStorage, ConflictResolvingStorage):
    ##
    # Implement conflict resolution for DemoStorage
    #

    def store(self, oid, serial, data, version, transaction):
        try:
            return super(DemoStorage, self).store(
                oid, serial, data, version, transaction)
        except ConflictError as e:
            old = e.serials[0]
            rdata = self.tryToResolveConflict(oid, old, serial, data)
            self.changes.store(oid, old, rdata, '', transaction)
            return ResolvedSerial

if not issubclass(_DemoStorage.DemoStorage, ConflictResolvingStorage):
    # BBB: ZODB < 4.3
    from ZODB.ConflictResolution import ResolvedSerial
    _DemoStorage.DemoStorage = DemoStorage
