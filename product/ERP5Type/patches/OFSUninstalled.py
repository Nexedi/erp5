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

# See https://launchpad.net/bugs/143531

from OFS import Uninstalled

if '__getstate__' not in Uninstalled.BrokenClass.__dict__:

  from ZODB.broken import persistentBroken, PersistentBroken
  from persistent import Persistent
  from threading import RLock
  Uninstalled.broken_klasses_lock = lock = RLock()
  Uninstalled_Broken = Uninstalled.Broken
  cache = Uninstalled.broken_klasses

  def Broken(self, oid, pair):
    lock.acquire()
    try:
      cached = pair in cache
      result = Uninstalled_Broken(self, oid, pair)
      if not cached:
        klass = cache.pop(pair)
        assert not issubclass(klass, PersistentBroken), \
          "This monkey-patch is not useful anymore"
        cache[pair] = persistentBroken(klass)
    finally:
      lock.release()
    return result

  Uninstalled.Broken = Broken
