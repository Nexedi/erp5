##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# Copyright (c) 2018 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from __future__ import absolute_import
import AccessControl.owner
from AccessControl import SpecialUsers as SU
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

# Patch description:
# Original method is called very often: multiple times per restricted python
# script/expression: once per __getattr__ (restricted getattr, actually) call.
# Each call pulls self's owner information, traverses to relevant user database
# and then use it to retrieve user object. These last two operations are
# expensive, and should produce the same result within a given transaction.
# So cache the first result for each owner tuple in a transactional cache.
UnownableOwner = AccessControl.owner.UnownableOwner
def getWrappedOwner(self):
    """Get the owner, modestly wrapped in the user folder.
    o If the object is not owned, return None.
    o If the owner's user database doesn't exist, return Nobody.
    o If the owner ID does not exist in the user database, return Nobody.
    """
    owner = self.getOwnerTuple()
    if owner is None or owner is UnownableOwner:
        return None
    udb_path, oid = owner
    cache_key = ('getWrappedOwner', ) + (
        (tuple(udb_path), oid)
        if isinstance(udb_path, list) else
        owner
    )
    try:
        return getTransactionalVariable()[cache_key]
    except KeyError:
        pass
    root = self.getPhysicalRoot()
    udb = root.unrestrictedTraverse(udb_path, None)
    if udb is None:
        result = SU.nobody
    else:
        user = udb.getUserById(oid, None)
        if user is None:
            result = SU.nobody
        else:
            result = user.__of__(udb)
    getTransactionalVariable()[cache_key] = result
    return result

AccessControl.owner.Owned.getWrappedOwner = getWrappedOwner
