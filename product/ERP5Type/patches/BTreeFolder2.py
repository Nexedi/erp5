##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# Stribger repair of BTreeFolder2
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from BTrees.OIBTree import OIBTree, union
from BTrees.Length import Length
from OFS.ObjectManager import BadRequestException, BeforeDeleteException
from Products.ZCatalog.Lazy import LazyMap
from zLOG import LOG, WARNING, ERROR, INFO

class ERP5BTreeFolder2Base(BTreeFolder2Base):
  """
    This class is only for backward compatibility.
  """
  pass

def _cleanup(self):
    """Cleans up errors in the BTrees.

    Certain ZODB bugs have caused BTrees to become slightly insane.
    Fortunately, there is a way to clean up damaged BTrees that
    always seems to work: make a new BTree containing the items()
    of the old one.

    Returns 1 if no damage was detected, or 0 if damage was
    detected and fixed.
    """
    from BTrees.check import check
    path = '/'.join(self.getPhysicalPath())
    try:
        check(self._tree)
        for key in list(self._tree.keys()):
            if key not in self._tree:
                raise AssertionError(
                    "Missing value for key: %s" % repr(key))
        check(self._mt_index)
        for key, object in list(self._tree.items()):
            meta_type = getattr(object, 'meta_type', None)
            if meta_type is not None:
              if meta_type not in self._mt_index:
                  raise AssertionError(
                      "Missing meta_type index for key: %s" % repr(key))
        for key, value in list(self._mt_index.items()):
            if (key not in self._mt_index
                or self._mt_index[key] is not value):
                raise AssertionError(
                    "Missing or incorrect meta_type index: %s"
                    % repr(key))
            check(value)
            for k in list(value.keys()):
                if k not in value or k not in self._tree:
                    raise AssertionError(
                        "Missing values for meta_type index: %s"
                        % repr(key))
        return 1
    except (AssertionError, KeyError):
        LOG('BTreeFolder2', WARNING,
            'Detected damage to %s. Fixing now.' % path,
            error=True)
        try:
            self._tree = OOBTree(self._tree)
            mt_index = OOBTree()
            for id, object in list(self._tree.items()):
              # Update the meta type index.
              meta_type = getattr(object, 'meta_type', None)
              if meta_type is not None:
                  ids = mt_index.get(meta_type, None)
                  if ids is None:
                      ids = OIBTree()
                      mt_index[meta_type] = ids
                  ids[id] = 1
            #LOG('Added All Object in BTree mti',0, map(lambda x:str(x), mt_index.keys()))
            self._mt_index = OOBTree(mt_index)
        except:
            LOG('BTreeFolder2', ERROR, 'Failed to fix %s.' % path,
                error=True)
            raise
        else:
            LOG('BTreeFolder2', INFO, 'Fixed %s.' % path)
        return 0

BTreeFolder2Base._cleanup = _cleanup

# Work around for the performance regression introduced in Zope 2.12.23.
# Otherwise, we use superclass' __contains__ implementation, which uses
# objectIds, which is inefficient in HBTreeFolder2 to lookup a single key.
BTreeFolder2Base.__contains__ = BTreeFolder2Base.has_key

# BBB: Remove workaround on recent BTreeFolder2Base
#      OFS.ObjectManager really needs to be fixed properly.
try:
  del BTreeFolder2Base.__getitem__
except AttributeError:
  pass
