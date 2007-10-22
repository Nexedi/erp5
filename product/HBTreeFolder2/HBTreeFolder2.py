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

import sys
from cgi import escape
from urllib import quote
from random import randint
from types import StringType

import Globals
from Globals import DTMLFile
from Globals import Persistent, PersistentMapping
from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from BTrees.OIBTree import OIBTree, union
from BTrees.Length import Length
from ZODB.POSException import ConflictError
from OFS.ObjectManager import BadRequestException, BeforeDeleteException
from OFS.Folder import Folder
from AccessControl import getSecurityManager, ClassSecurityInfo
from AccessControl.Permissions import access_contents_information, \
     view_management_screens
from zLOG import LOG, INFO, ERROR, WARNING
from Products.ZCatalog.Lazy import LazyMap, LazyFilter, LazyCat


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


class HBTreeFolder2Base (Persistent):
    """Base for BTree-based folders.
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
    _tree_list = None


    def __init__(self, id=None):
        if id is not None:
            self.id = id
        self._initBTrees()

    def _initBTrees(self):
        self._htree = OOBTree()
        self._count = Length()
        self._tree_list = PersistentMapping()

    def initBTrees(self):
        """ """
        return self._initBTrees()

    def _populateFromFolder(self, source):
        """Fill this folder with the contents of another folder.
        """
        for name in source.objectIds():
            value = source._getOb(name, None)
            if value is not None:
                self._setOb(name, aq_base(value))


    security.declareProtected(view_management_screens, 'manage_fixCount')
    def manage_fixCount(self):
        """Calls self._fixCount() and reports the result as text.
        """
        old, new = self._fixCount()
        path = '/'.join(self.getPhysicalPath())
        if old == new:
            return "No count mismatch detected in HBTreeFolder2 at %s." % path
        else:
            return ("Fixed count mismatch in HBTreeFolder2 at %s. "
                    "Count was %d; corrected to %d" % (path, old, new))


    def _fixCount(self):
        """Checks if the value of self._count disagrees with
        len(self.objectIds()). If so, corrects self._count. Returns the
        old and new count values. If old==new, no correction was
        performed.
        """
        old = self._count()
        new = len(self.objectIds())
        if old != new:
            self._count.set(new)
        return old, new


    security.declareProtected(view_management_screens, 'manage_cleanup')
    def manage_cleanup(self):
        """Calls self._cleanup() and reports the result as text.
        """
        v = self._cleanup()
        path = '/'.join(self.getPhysicalPath())
        if v:
            return "No damage detected in HBTreeFolder2 at %s." % path
        else:
            return ("Fixed HBTreeFolder2 at %s.  "
                    "See the log for more details." % path)


    def _cleanup(self):
        """Cleans up errors in the BTrees.

        Certain ZODB bugs have caused BTrees to become slightly insane.
        Fortunately, there is a way to clean up damaged BTrees that
        always seems to work: make a new BTree containing the items()
        of the old one.

        Returns 1 if no damage was detected, or 0 if damage was
        detected and fixed.
        """
        def hCheck(htree):
          """
              Recursively check the btree
          """
          check(htree)
          for key in htree.keys():
              if not htree.has_key(key):
                  raise AssertionError(
                      "Missing value for key: %s" % repr(key))
              else:
                ob = htree[key]
                if isinstance(ob, OOBTree):
                  hCheck(ob)
          return 1
        
        from BTrees.check import check
        path = '/'.join(self.getPhysicalPath())
        try:
            return hCheck(self._htree)
        except AssertionError:            
            LOG('HBTreeFolder2', WARNING,
                'Detected damage to %s. Fixing now.' % path,
                error=sys.exc_info())
            try:
                self._htree = OOBTree(self._htree) # XXX hFix needed
            except:
                LOG('HBTreeFolder2', ERROR, 'Failed to fix %s.' % path,
                    error=sys.exc_info())
                raise
            else:
                LOG('HBTreeFolder2', INFO, 'Fixed %s.' % path)
            return 0

    def hashId(self, id):
        """Return a tuple of ids
        """
        id_list = str(id).split(H_SEPARATOR)     # We use '-' as the separator by default
        if len(id_list) > 1:
          return tuple(id_list)
        else:
          return [id,]
    
#         try:                             # We then try int hashing
#           id_int = int(id)
#         except ValueError:
#           return id_list
#         result = []
#         while id_int:
#           result.append(id_int % MAX_OBJECT_PER_LEVEL)
#           id_int = id_int / MAX_OBJECT_PER_LEVEL
#         result.reverse()
#         return tuple(result)

    def _getOb(self, id, default=_marker):
        """
            Return the named object from the folder.
        """
        htree = self._htree
        ob = htree
        id_list = self.hashId(id)
        for sub_id in id_list[0:-1]:
          if default is _marker:
            ob = ob[sub_id]
          else:
            ob = ob.get(sub_id, _marker)
            if ob is _marker:
              return default
        if default is _marker:
          ob = ob[id]
        else:
          ob = ob.get(id, _marker)
          if ob is _marker:
            return default
        return ob.__of__(self)

    def _setOb(self, id, object):
        """Store the named object in the folder.
        """
        htree = self._htree
        id_list = self.hashId(id)
        for idx in xrange(len(id_list) - 1):
          sub_id = id_list[idx]
          if sub_id not in htree:
            # Create a new level
            htree[sub_id] = OOBTree()
            if isinstance(sub_id, (int, long)):
              tree_id = 0
              for id in id_list[:idx+1]:
                  tree_id = tree_id + id * MAX_OBJECT_PER_LEVEL
            else:
              tree_id = H_SEPARATOR.join(id_list[:idx+1])
            # Index newly created level
            self._tree_list[tree_id] = None
            
          htree = htree[sub_id]
        # set object in subtree
        ob_id = id_list[-1]
        if htree.has_key(id):
            raise KeyError('There is already an item named "%s".' % id)
        htree[id] = object
        self._count.change(1)

    def _delOb(self, id):
        """Remove the named object from the folder.
        """
        htree = self._htree
        id_list = self.hashId(id)
        for sub_id in id_list[0:-1]:
          htree = htree[sub_id]
        del htree[id]
        self._count.change(-1)

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
        idlist = self.objectIds()  # Pre-sorted.
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

        formatted = []
        formatted.append(listtext0 % pref_rows)
        for i in range(b_start - 1, b_end):
            optID = escape(idlist[i])
            formatted.append(listtext1 % (escape(optID, quote=1), optID))
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
        htree = self._htree
        id_list = self.hashId(id)
        for sub_id in id_list[0:-1]:
          if not isinstance(htree, OOBTree):
            return 0
          if not htree.has_key(sub_id):
            return 0
          htree = htree[sub_id]
        if not htree.has_key(id):
          return 0
        return 1


    security.declareProtected(access_contents_information,
                              'treeIds')
    def treeIds(self, base_id=None):
        """ Return a list of subtree ids
        """
        tree = self._getTree(base_id=base_id)
        return [x for x in self._htree.keys() if isinstance(self._htree[x], OOBTree)]


    def _getTree(self, base_id):
        """ Return the tree wich has the base_id
        """
        htree = self._htree
        id_list = self.hashId(base_id)
        for sub_id in id_list:            
          if not isinstance(htree, OOBTree):
            return None
          if not htree.has_key(sub_id):
            raise IndexError, base_id
          htree = htree[sub_id]
        return htree

    def _getTreeIdList(self, htree=None):
        """ recursively build a list of btree ids
        """
        if htree is None:
          htree = self._htree
          btree_list = [None,]
        else:
            btree_list = []
        for obj_id in htree.keys():
          obj = htree[obj_id]
          if isinstance(obj, OOBTree):
            btree_list.extend(["%s-%s"%(obj_id, x) for x in self._getTreeIdList(htree=obj)])
            btree_list.append(obj_id)

        return btree_list 

    security.declareProtected(access_contents_information,
                              'getTreeIdList')
    def getTreeIdList(self, htree=None):
        """ Return list of all tree ids
        """
        if self._tree_list is None or len(self._tree_list.keys()) == 0:
            tree_list = self._getTreeIdList(htree=htree)
            self._tree_list = PersistentMapping()
            for tree in tree_list:                
                self._tree_list[tree] = None
        return sorted(self._tree_list.keys())


    def _treeObjectValues(self, base_id=None):
        """ return object values for a given btree
        """
        if base_id is not None:
            return LazyFilter(self._isNotBTree, self._getTree("%s" %base_id).values())
        else:
            return LazyFilter(self._isNotBTree, self._htree.values())

    def _treeObjectIds(self, base_id=None):
        """ return object ids for a given btree
        """
        if base_id is not None:
          return LazyFilter(self._checkObjectId, self._getTree("%s" %base_id).keys())
        else:
          return LazyFilter(self._checkObjectId, self._htree.keys())

    def _isNotBTree(self, obj):
        """ test object is not a btree
        """
        if isinstance(obj, OOBTree):
            return False
        else:
            return True

    def _checkObjectId(self, id):
        """ test id is not in btree id list
        """
        return not self._tree_list.has_key(id)
        
    security.declareProtected(access_contents_information,
                              'ObjectValues')
    def objectValues(self, base_id=_marker, spec=None):
        return LazyMap(self._getOb, self.objectIds(base_id))


    security.declareProtected(access_contents_information,
                              'objectIds')
    def objectIds(self, base_id=_marker, spec=None):
        if base_id is _marker:
            return LazyCat(LazyMap(self._treeObjectIds, self.getTreeIdList()))
        else:
            return self._treeObjectIds(base_id=base_id)

    
    security.declareProtected(access_contents_information,
                              'objectItems')
    def objectItems(self, base_id=_marker, spec=None):
        # Returns a list of (id, subobject) tuples of the current object.
        # If 'spec' is specified, returns only objects whose meta_type match
        # 'spec'
        return LazyMap(lambda id, _getOb=self._getOb: (id, _getOb(id)),
                       self.objectIds(base_id, spec))


    security.declareProtected(access_contents_information,
                              'objectMap')
    def objectMap(self):
        # Returns a tuple of mappings containing subobject meta-data.
        return LazyMap(lambda (k, v):
                       {'id': k, 'meta_type': getattr(v, 'meta_type', None)},
                       self._htree.items(), self._count())

    # superValues() looks for the _objects attribute, but the implementation
    # would be inefficient, so superValues() support is disabled.
    _objects = ()


    security.declareProtected(access_contents_information,
                              'objectIds_d')
    def objectIds_d(self, t=None):
        ids = self.objectIds(t)
        res = {}
        for id in ids:
            res[id] = 1
        return res


    security.declareProtected(access_contents_information,
                              'objectMap_d')
    def objectMap_d(self, t=None):
        return self.objectMap()


    def _checkId(self, id, allow_dup=0):
        if not allow_dup and self.has_key(id):
            raise BadRequestException, ('The id "%s" is invalid--'
                                        'it is already in use.' % id)


    def _setObject(self, id, object, roles=None, user=None, set_owner=1):
        v=self._checkId(id)
        if v is not None: id=v

        # If an object by the given id already exists, remove it.
        if self.has_key(id):
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
        except BeforeDeleteException, ob:
            raise
        except ConflictError:
            raise
        except:
            LOG('Zope', ERROR, 'manage_beforeDelete() threw',
                error=sys.exc_info())
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
        return self._getOb(name, default)


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
                if not tree.has_key(id):
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
        res = self._getOb(name, None)
        if res is None:
            raise AttributeError, name
        return res


Globals.InitializeClass(HBTreeFolder2Base)


class HBTreeFolder2 (HBTreeFolder2Base, Folder):
    """BTreeFolder2 based on OFS.Folder.
    """
    meta_type = 'HBTreeFolder2'

    def _checkId(self, id, allow_dup=0):
        Folder._checkId(self, id, allow_dup)
        HBTreeFolder2Base._checkId(self, id, allow_dup)
    

Globals.InitializeClass(HBTreeFolder2)

