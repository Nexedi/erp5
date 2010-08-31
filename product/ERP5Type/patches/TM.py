##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import transaction
from Shared.DC.ZRDB.TM import TM, Surrogate


# ZPublisher error path can aggravate error:
#   https://bugs.launchpad.net/bugs/229863

def TM__register(self):
    if not self._registered:
        #try:
            transaction.get().register(Surrogate(self))
            self._begin()
            self._registered = 1
            self._finalize = 0
        #except: pass

TM._register = TM__register

if getattr(TM, 'setSortKey', None) is None:

    # BACK: We're not yet on Zope 2.12, patch in the sort_key setting method
    # remove this part when we drop support for earlier versions.
    def setSortKey(self, sort_key):
        self._sort_key = sort_key

    def sortKey(self, *ignored):
        """ The sortKey method is used by the transaction subsystem to have a
            known commit order for lock acquisition.
        """
        return self._sort_key

    TM._sort_key = 1
    TM.setSortKey = setSortKey
    TM.sortKey = sortKey

