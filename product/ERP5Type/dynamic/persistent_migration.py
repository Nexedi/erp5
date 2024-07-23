##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                    Julien Muchembled <jm@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

# The class of an object is first fixed non-persistently by __setstate__:
# - It can't be done before because its portal_type maybe different from
#   the one specified on the old class.
# - If done later, some methods may be wrong or missing.
# By default, objects are not migrated persistently, mainly because the old
# class may be copied in the pickle of the container, and we can't access it
# from __setstate__.

import logging, re
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from OFS.Folder import Folder as OFS_Folder
from persistent import Persistent, wref
from ZODB.serialize import ObjectWriter, ObjectReader
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base, TempBase, WorkflowMethod
from zodbpickle import binary
import six


log = logging.getLogger('ERP5Type')
log.trace = lambda *args, **kw: log.log(5, *args, **kw)

isOldBTree = re.compile(r'BTrees\._(..)BTree\.(\1)BTree$').match

class Ghost(object):

  def __init__(self, oid):
    self._p_oid = oid

class LazyPersistent(object):

  def __call__(self, oid):
    return Ghost(oid)

class LazyBTree(LazyPersistent):
  """Fake class to prevent loading too many objects while migrating BTrees

  When we don't migrate recursively, we don't want to migrate values of BTrees,
  and for performance reasons, we don't even want to load them.
  So the only remaining way to know if a BTree contains BTrees/Buckets or values
  is to look at how the state is structured.
  """

  def getOidList(self, state):
    if state and len(state) > 1:
      # return oid of first/next bucket
      return state[1]._p_oid,
    return ()

class PickleUpdater(ObjectReader, ObjectWriter, object):
  """Function-like class to update obsolete references in pickle"""

  def __new__(cls, obj, recursive=False):
    self = object.__new__(cls)
    obj = aq_base(obj)
    connection = obj._p_jar
    ObjectReader.__init__(self, connection, connection._cache,
                                connection._db.classFactory)
    ObjectWriter.__init__(self, obj)
    migrated_oid_set = set()
    oid_set = {obj._p_oid}
    while oid_set:
      oid = oid_set.pop()
      obj = ObjectReader.load_oid(self, oid)
      obj._p_activate()
      klass = obj.__class__
      self.lazy = None
      if not recursive:
        _setOb = getattr(klass, '_setOb', None)
        if _setOb:
          if isinstance(_setOb, WorkflowMethod):
            _setOb = _setOb._m
          if six.get_unbound_function(_setOb) is six.get_unbound_function(OFS_Folder._setOb):
            self.lazy = Ghost
        elif klass.__module__[:7] == 'BTrees.' and klass.__name__ != 'Length':
          self.lazy = LazyBTree()
      self.oid_dict = {}
      self.oid_set = set()
      try:
        p, serial = self._conn._storage.load(oid, '')
      except TypeError:
        # MVCCAdapter of ZODB5
        p, serial = self._conn._storage.load(oid)
      unpickler = self._get_unpickler(p)
      def find_global(*args):
        self.do_migrate = args != (klass.__module__, klass.__name__) and \
                          not isOldBTree('%s.%s' % args)
        unpickler.find_global = self._get_class
        if six.PY3:
          unpickler.find_class = self._get_class
        return self._get_class(*args)
      unpickler.find_global = find_global
      if six.PY3:
        unpickler.find_class = find_global
      unpickler.load() # class
      state = unpickler.load()
      if isinstance(self.lazy, LazyPersistent):
        self.oid_set.update(self.lazy.getOidList(state))
      migrated_oid_set.add(oid)
      oid_set |= self.oid_set - migrated_oid_set
      self.oid_set = None
      if self.do_migrate:
        log.debug('PickleUpdater: migrate %r (%r)', obj, klass)
        self.setGhostState(obj, self.serialize(obj))
        obj._p_changed = 1

  def getOid(self, obj):
    if isinstance(obj, (Persistent, type, wref.WeakRef)):
      return getattr(obj, '_p_oid', None)

  def load_oid(self, oid):
    if self.oid_set is not None:
      if self.lazy:
        return self.lazy(oid)
      self.oid_set.add(oid)
    return ObjectReader.load_oid(self, oid)

  def load_persistent(self, oid, klass):
    obj = ObjectReader.load_persistent(self, oid, klass)
    if self.oid_set is not None:
      if not self.lazy:
        self.oid_set.add(oid)
      obj._p_activate()
      self.oid_dict[oid] = oid_klass = ObjectWriter.persistent_id(self, obj)
      if oid_klass != (oid, klass):
        self.do_migrate = True
    return obj

  def persistent_id(self, obj):
    assert type(obj) is not Ghost
    oid = self.getOid(obj)
    if isinstance(oid, (bytes, binary)):
      try:
        return self.oid_dict[oid]
      except KeyError:
        obj._p_activate()
    return ObjectWriter.persistent_id(self, obj)

if 1:
  from Products.ERP5Type.Core.Folder import Folder
  from Products.ERP5.Tool.CategoryTool import CategoryTool

  Base__setstate__ = Base.__setstate__

  def __setstate__(self, value):
    klass = self.__class__

    if klass.__module__ in ('erp5.portal_type', 'erp5.temp_portal_type'):
      return Base__setstate__(self, value)
    if klass is TempBase:
      return Base__setstate__(self, value)
    try:
      portal_type = value.get('portal_type') or klass.portal_type
    except AttributeError:
      log.warn("no portal type was found for %r (class %s)", self, klass)
      return Base__setstate__(self, value)
    # proceed with migration
    try:
      self._fixPortalTypeBeforeMigration(portal_type)
    except IndexError: # getSite raised
      return Base__setstate__(self, value)
    import erp5.portal_type
    newklass = getattr(erp5.portal_type, portal_type)
    assert self.__class__ is not newklass
    self.__class__ = newklass
    self.__setstate__(value)
    log.trace("Base.__setstate__: migrate %r", self)

  def migrateToPortalTypeClass(self, recursive=False):
    """Migrate persistently all referenced classes

    When 'recursive' is False, subobjects (read objectValues) are not migrated.
    So a typical migration of a big folder using activities would be:

      folder.migrateToPortalTypeClass()
      for obj in folder.objectValues():
        obj.activate().migrateToPortalTypeClass(True)

    Note however this pattern does not work for HBTrees, because sub-btrees are
    treated like subobjects for PickleUpdater.
    """
    PickleUpdater(self, recursive)

  Base.__setstate__ = __setstate__
  Folder.__setstate__ = CategoryTool.__setstate__ = __setstate__
  Base._fixPortalTypeBeforeMigration = lambda self, portal_type: None
  Base.migrateToPortalTypeClass = migrateToPortalTypeClass
  Base.security.declareProtected(Permissions.ManagePortal,
                                 'migrateToPortalTypeClass')

else:
  __setstate__ = None
