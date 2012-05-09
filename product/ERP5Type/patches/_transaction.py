############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################

# XXX: This file starts with an underscore because by default, on Python 2.6,
#      imports are relative.

from time import time
from transaction import _manager

def _new_transaction(txn, synchs):
    txn.start_time = time()
    if synchs:
        synchs.map(lambda s: s.newTransaction(txn))

_manager._new_transaction = _new_transaction
