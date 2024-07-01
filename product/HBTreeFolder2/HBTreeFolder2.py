##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

import operator
from Products.PythonScripts.standard import html_quote
from itertools import chain, islice
import six
try:
  from itertools import imap as map
except ImportError: # six.PY3
  pass
from six.moves.urllib.parse import quote
from random import randint
from six.moves import xrange

from AccessControl.class_init import InitializeClass
from App.special_dtml import DTMLFile
from Persistence import Persistent, PersistentMapping
from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from BTrees.Length import Length
from ZODB.POSException import ConflictError
from OFS.ObjectManager import BadRequestException, BeforeDeleteException
from OFS.Folder import Folder
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permissions import access_contents_information, \
     view_management_screens
from zLOG import LOG, ERROR
from AccessControl.SimpleObjectPolicies import ContainerAssertions


manage_addHBTreeFolder2Form = DTMLFile('folderAdd', globals())

def manage_addHBTreeFolder2(dispatcher, id, title='', REQUEST=None):
    """Adds a new HBTreeFolder object with id *id*.
    """
    id = str(id)
    ob = HBTreeFolder2(id)
    ob.title = str(title)
    dispatcher._setObject(id, ob)
    ob = dispatcher._getOb(id)
    if REQUEST is not None:
        return dispatcher.manage_main(dispatcher, REQUEST, update_menu=1)


listtext0 = '''<select name="ids:list" multiple="multiple" size="%s">
'''
listtext1 = '''<option value="%s">%s</option>
'''
listtext2 = '''</select>
'''


_marker = []  # Create a new marker object.

MAX_UNIQUEID_ATTEMPTS = 1000
MAX_OBJECT_PER_LEVEL = 1000
H_SEPARATOR = '-'

class ExhaustedUniqueIdsError (Exception):
    pass


class HBTreeObjectIds(object):

    _index = float('inf')
    _items = tuple

    def __init__(self, tree, base_id=_marker):
        if base_id is _marker:
            self._count = tree._count
            self._items = tree._htree_iteritems
            return
        h = tree._htree
        if base_id:
            try:
                for sub_id in tree.hashId(base_id):
                    h = h[sub_id]
                    if type(h) is not OOBTree:
                        return
            except KeyError:
                return
        self._items = lambda: (i for i in six.iteritems(h)
                                 if type(i[1]) is not OOBTree)

    def _count(self):
        count = sum(1 for x in self._items())
        self._count = lambda: count
        return count

    def __len__(self):
        return self._count()

    def __iter__(self):
        return map(self._item_result, self._items())

    _item_result = operator.itemgetter(0)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return [self.__getitem__(x) for x in xrange(*item.indices(self._count()))]
        if item < 0:
            item += self._count()
        i = self._index
        self._index = item + 1
        i = item - i
        if i < 0:
            self._iitems = items = self._items()
            i = islice(items, item, None)
        elif i:
            i = islice(self._iitems, i, None)
        else:
            i = self._iitems
        try:
            return self._item_result(next(i))
        except StopIteration:
            del self._index, self._iitems
            raise IndexError

ContainerAssertions[HBTreeObjectIds] = 1

class HBTreeObjectItems(HBTreeObjectIds):

    def __init__(self, tree, base_id=_marker):
        HBTreeObjectIds.__init__(self, tree, base_id)
        self._item_result = lambda item: (item[0], item[1].__of__(tree))

ContainerAssertions[HBTreeObjectItems] = 1

class HBTreeObjectValues(HBTreeObjectIds):

    def __init__(self, tree, base_id=_marker):
        HBTreeObjectIds.__init__(self, tree, base_id)
        self._item_result = lambda item: item[1].__of__(tree)

ContainerAssertions[HBTreeObjectValues] = 1


class HBTreeFolder2Base (Persistent):
    """Base for BTree-based folders.

    BUG: Due to wrong design, we can't store 2 objects <A> and <A>-<B>
         where <A> does not contain '-'. We detect conflicts at the
         root level using 'type(ob) is OOBTree'
    """

    security = ClassSecurityInfo()

    manage_options=(
        ({'label':'Contents', 'action':'manage_main',},
         ) + Folder.manage_options[1:]
        )

    security.declareProtected(view_management_screens,
                              'manage_main')
    manage_main = DTMLFile('contents', globals())

    _htree = None      # OOBTree: { id -> object }
    _count = None     # A BTrees.Length
    _v_nextid = 0     # The integer component of the next generated ID
    title = ''


    def __init__(self, id=None):
        if id is not None:
            self.id = id
        self._initBTrees()

    def _initBTrees(self):
        self._htree = OOBTree()
        self._count = Length()

    def _populateFromFolder(self, source):
        """Fill this folder with the contents of another folder.
        """
        for name, value in source.objectItems():
            self._setOb(name, aq_base(value))

    security.declareProtected(view_management_screens, 'manage_fixCount')
    def manage_fixCount(self, dry_run=0):
        """Calls self._fixCount() and reports the result as text.
        """
        old, new = self._fixCount(dry_run)
        path = '/'.join(self.getPhysicalPath())
        if old == new:
            return "No count mismatch detected in HBTreeFolder2 at %s." % path
        else:
            return ("Fixed count mismatch in HBTreeFolder2 at %s. "
                    "Count was %d; corrected to %d" % (path, old, new))


    def _fixCount(self, dry_run=0):
        """Checks if the value of self._count disagrees with the content of
        the htree. If so, corrects self._count. Returns the old and new count
        values. If old==new, no correction was performed.
        """
        old = self._count()
        new = sum(1 for x in self._htree_iteritems())
        if old != new and not dry_run:
            self._count.set(new)
        return old, new

    def hashId(self, id):
        return id.split(H_SEPARATOR)

    def _htree_get(self, id):
        id_list = self.hashId(id)
        if len(id_list) == 1:
          ob = self._htree[id]
          if type(ob) is OOBTree:
            raise KeyError
        else:
          ob = self._htree[id_list.pop(0)]
          if type(ob) is not OOBTree:
            raise KeyError
          id_list[-1] = id
          for sub_id in id_list:
            ob = ob[sub_id]
        return ob

    def _getOb(self, id, default=_marker):
        """Return the named object from the folder
        """
        try:
          return self._htree_get(id).__of__(self)
        except KeyError:
          if default is _marker:
            raise KeyError(id)
        return default

    def __getitem__(self, id):
        try:
          return self._htree_get(id).__of__(self)
        except KeyError:
          raise KeyError(id)

    def _setOb(self, id, object):
        """Store the named object in the folder.
        """
        if type(object) is OOBTree:
          raise ValueError('HBTreeFolder2 can not store OOBTree objects')
        htree = self._htree
        for sub_id in self.hashId(id)[:-1]:
          try:
            htree = htree[sub_id]
          except KeyError:
            htree[sub_id] = htree = OOBTree()
            continue
          if type(htree) is not OOBTree:
            assert self._htree[sub_id] is htree, (htree, id)
            raise KeyError('There is already an item whose id is %r' % sub_id)
        if id in htree:
          raise KeyError('There is already an item named %r.' % id)
        htree[id] = object
        self._count.change(1)

    def _delOb(self, id):
        """Remove the named object from the folder.
        """
        htree = self._htree
        h = []
        for sub_id in self.hashId(id)[:-1]:
          h.append((htree, sub_id))
          htree = htree.get(sub_id)
          if type(htree) is not OOBTree:
            raise KeyError(id)
        if type(htree[id]) is OOBTree:
          raise KeyError(id)
        del htree[id]
        self._count.change(-1)
        while h and not htree:
          htree, sub_id = h.pop()
          del htree[sub_id]

    security.declareProtected(view_management_screens, 'getBatchObjectListing')
    def getBatchObjectListing(self, REQUEST=None):
        """Return a structure for a page template to show the list of objects.
        """
        if REQUEST is None:
            REQUEST = {}
        pref_rows = int(REQUEST.get('dtpref_rows', 20))
        b_start = int(REQUEST.get('b_start', 1))
        b_count = int(REQUEST.get('b_count', 1000))
        b_end = b_start + b_count - 1
        url = self.absolute_url() + '/manage_main'
        count = self.objectCount()

        if b_end < count:
            next_url = url + '?b_start=%d' % (b_start + b_count)
        else:
            b_end = count
            next_url = ''

        if b_start > 1:
            prev_url = url + '?b_start=%d' % max(b_start - b_count, 1)
        else:
            prev_url = ''

        formatted = [listtext0 % pref_rows]
        for optID in islice(self.objectIds(), b_start - 1, b_end):
            optID = html_quote(optID)
            formatted.append(listtext1 % (html_quote(optID), optID))
        formatted.append(listtext2)
        return {'b_start': b_start, 'b_end': b_end,
                'prev_batch_url': prev_url,
                'next_batch_url': next_url,
                'formatted_list': ''.join(formatted)}


    security.declareProtected(view_management_screens,
                              'manage_object_workspace')
    def manage_object_workspace(self, ids=(), REQUEST=None):
        '''Redirects to the workspace of the first object in
        the list.'''
        if ids and REQUEST is not None:
            REQUEST.RESPONSE.redirect(
                '%s/%s/manage_workspace' % (
                self.absolute_url(), quote(ids[0])))
        else:
            return self.manage_main(self, REQUEST)


    security.declareProtected(access_contents_information,
                              'tpValues')
    def tpValues(self):
        """Ensures the items don't show up in the left pane.
        """
        return ()


    security.declareProtected(access_contents_information,
                              'objectCount')
    def objectCount(self):
        """Returns the number of items in the folder."""
        return self._count()


    security.declareProtected(access_contents_information, 'has_key')
    def has_key(self, id):
        """Indicates whether the folder has an item by ID.
        """
        try:
          self._htree_get(id)
        except KeyError:
          return 0
        return 1

    # Work around for the performance regression introduced in Zope 2.12.23.
    # Otherwise, we use superclass' __contains__ implementation, which uses
    # objectIds, which is inefficient in HBTreeFolder2 to lookup a single key.
    __contains__ = has_key

    def _htree_iteritems(self, min=None):
        # BUG: Due to bad design of HBTreeFolder2, buckets other than the root
        #      one must not contain both buckets & leafs. Otherwise, this method
        #      fails.
        h = self._htree
        recurse_stack = []
        try:
          for sub_id in self.hashId(min) if min else ('',):
            if recurse_stack:
              next(i)
              if type(h) is not OOBTree:
                break
              id += H_SEPARATOR + sub_id
              if type(next(six.itervalues(h))) is not OOBTree:
                sub_id = id
            else:
              id = sub_id
            i = h.iteritems(sub_id)
            recurse_stack.append(i)
            h = h[sub_id]
        except (KeyError, StopIteration):
          pass
        while recurse_stack:
          i = recurse_stack.pop()
          try:
            while 1:
              id, h = next(i)
              if type(h) is OOBTree:
                recurse_stack.append(i)
                i = six.iteritems(h)
              else:
                yield id, h
          except StopIteration:
            pass

    security.declareProtected(access_contents_information,
                              'getTreeIdList')
    def getTreeIdList(self, htree=None):
        """ Return list of all tree ids
        """
        r = []
        s = [(None, six.iteritems(self._htree))]
        while s:
          base_id, items = s.pop()
          if base_id:
            for k, v in items:
              if type(v) is not OOBTree:
                r.append(base_id)
                # As an optimization, and because _htree_iteritems does not
                # support mixed buckets except at the root, we consider that
                # this one only contains leafs.
                break
              s.append((base_id + H_SEPARATOR + k, six.iteritems(v)))
          else:
            for k, v in items:
              if type(v) is not OOBTree:
                r.append(base_id)
                for k, v in items:
                  if type(v) is OOBTree:
                    s.append((k, six.iteritems(v)))
                break
              s.append((k, six.iteritems(v)))
        if six.PY2:
          r.sort()
        else:
          r.sort(key=lambda e: '' if e is None else e)
        return r

    security.declareProtected(access_contents_information,
                              'objectValues')
    def objectValues(self, base_id=_marker):
        return HBTreeObjectValues(self, base_id)

    security.declareProtected(access_contents_information,
                              'objectIds')
    def objectIds(self, base_id=_marker):
        return HBTreeObjectIds(self, base_id)

    security.declareProtected(access_contents_information,
                              'objectItems')
    def objectItems(self, base_id=_marker):
        # Returns a list of (id, subobject) tuples of the current object.
        return HBTreeObjectItems(self, base_id)

    # superValues() looks for the _objects attribute, but the implementation
    # would be inefficient, so superValues() support is disabled.
    _objects = ()


    security.declareProtected(access_contents_information,
                              'objectIds_d')
    def objectIds_d(self, t=None):
        return dict.fromkeys(self.objectIds(t), 1)

    def _checkId(self, id, allow_dup=0):
        if not allow_dup and id in self:
            raise BadRequestException(
                'The id %r is invalid--it is already in use.' % id)


    def _setObject(self, id, object, roles=None, user=None, set_owner=1):
        v=self._checkId(id)
        if v is not None: id=v

        # If an object by the given id already exists, remove it.
        if id in self:
            self._delObject(id)

        self._setOb(id, object)
        object = self._getOb(id)

        if set_owner:
            object.manage_fixupOwnershipAfterAdd()

            # Try to give user the local role "Owner", but only if
            # no local roles have been set on the object yet.
            if hasattr(object, '__ac_local_roles__'):
                if object.__ac_local_roles__ is None:
                    user=getSecurityManager().getUser()
                    if user is not None:
                        userid=user.getId()
                        if userid is not None:
                            object.manage_setLocalRoles(userid, ['Owner'])

        object.manage_afterAdd(object, self)
        return id


    def _delObject(self, id, dp=1):
        object = self._getOb(id)
        try:
            object.manage_beforeDelete(object, self)
        except BeforeDeleteException as ob:
            raise
        except ConflictError:
            raise
        except Exception:
            LOG('Zope', ERROR, 'manage_beforeDelete() threw',
                error=True)
        self._delOb(id)


    # Aliases for mapping-like access.
    __len__ = objectCount
    keys = objectIds
    values = objectValues
    items = objectItems

    # backward compatibility
    hasObject = has_key

    security.declareProtected(access_contents_information, 'get')
    def get(self, name, default=None):
        try:
          return self._htree_get(name).__of__(self)
        except KeyError:
          return default

    # Utility for generating unique IDs.

    security.declareProtected(access_contents_information, 'generateId')
    def generateId(self, prefix='item', suffix='', rand_ceiling=999999999):
        """Returns an ID not used yet by this folder.

        The ID is unlikely to collide with other threads and clients.
        The IDs are sequential to optimize access to objects
        that are likely to have some relation.
        """
        tree = self._htree
        n = self._v_nextid
        attempt = 0
        while 1:
            if n % 4000 != 0 and n <= rand_ceiling:
                id = '%s%d%s' % (prefix, n, suffix)
                if id not in tree:
                    break
            n = randint(1, rand_ceiling)
            attempt = attempt + 1
            if attempt > MAX_UNIQUEID_ATTEMPTS:
                # Prevent denial of service
                raise ExhaustedUniqueIdsError
        self._v_nextid = n + 1
        return id

    def __getattr__(self, name):
        # Boo hoo hoo!  Zope 2 prefers implicit acquisition over traversal
        # to subitems, and __bobo_traverse__ hooks don't work with
        # restrictedTraverse() unless __getattr__() is also present.
        # Oh well.
        try:
            return self._htree_get(name)
        except KeyError:
            raise AttributeError(name)


InitializeClass(HBTreeFolder2Base)


class HBTreeFolder2 (HBTreeFolder2Base, Folder):
    """BTreeFolder2 based on OFS.Folder.
    """
    meta_type = 'HBTreeFolder2'

    def _checkId(self, id, allow_dup=0):
        Folder._checkId(self, id, allow_dup)
        HBTreeFolder2Base._checkId(self, id, allow_dup)


InitializeClass(HBTreeFolder2)

