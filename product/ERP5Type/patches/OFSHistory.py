##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from OFS.History import HystoryJar, historicalRevision

"""
Rationale for this patch:
Modifications __setstate__ does to self must not cause object to become
registered to its jar (ie, it must have no jar).

Original code breaks this, and this makes it impossible to view, for example,
a former revision of a PythonScript if that revision was written by an old
Zope (ex: 2.12 reading 2.8 PythonScript).

Launchpad bug opened, patch submitted:
  https://bugs.launchpad.net/zope2/+bug/735999
"""

# Original function lines removed by this patch are present but commented-out.
def patched_historicalRevision(self, serial):
    state=self._p_jar.oldstate(self, serial)
    rev=self.__class__.__basicnew__()
#    rev._p_jar=HystoryJar(self._p_jar)
    rev._p_oid=self._p_oid
#    rev._p_serial=serial
    rev.__setstate__(state)
#    rev._p_changed=0
# PATCH ADDITION BEGIN
    rev._p_serial=serial
    rev._p_jar=HystoryJar(self._p_jar)
# PATCH ADDITION END
    return rev

historicalRevision.__code__ = patched_historicalRevision.__code__

