##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.Globals import InitializeClass, PersistentMapping
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import cartesianProduct, INFINITE_SET
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter

from zLOG import LOG


class Matrix(object):
  """A mix-in class which provides a matrix like access to objects.

  Matrices are of any dimension.

  A single Matrix may contain multiple matrices, of different dimension.
  Each matrix is associated to a so-called 'base_id'.
  """

  # Declarative security
  security = ClassSecurityInfo()

  # Matrix Methods
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCell' )
  def getCell(self, *kw , **kwd):
    """Access a cell by its coordinates and base_id.
    """
    if getattr(aq_base(self), 'index', None) is None:
      return None

    base_id = kwd.get('base_id', "cell")
    if not self.index.has_key(base_id):
      return None

    cell_id = self.keyToId(kw, base_id = base_id)
    if cell_id is None:
      return None
    return self.get(cell_id)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCellProperty' )
  def getCellProperty(self, *kw , **kwd):
    """Get a property of a cell by its coordinates and base_id.
    """
    base_id= kwd.get('base_id', "cell")
    cell = self.getCell(*kw, **kwd)
    if cell is None:
      return None

    return cell.getProperty(base_id)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'hasCell' )
  def hasCell(self, *kw , **kwd):
    """Checks if matrix corresponding to base_id contains cell specified by
    *kw coordinates.
    """
    return self.getCell(*kw, **kwd) is not None

  security.declareProtected( Permissions.AccessContentsInformation,
                             'hasCellContent' )
  def hasCellContent(self, base_id='cell'):
    """
        Checks if matrix corresponding to base_id contains cells.
    """
    aq_self = aq_base(self)

    if getattr(aq_self, 'index', None) is None:
      return 0

    if not self.index.has_key(base_id):
      return 0

    for i in self.getCellIds(base_id=base_id):
      if hasattr(self, i): # We should try to use aq_self if possible but XXX
        return 1

    return 0

  security.declareProtected( Permissions.AccessContentsInformation,
                             'hasInRange' )
  def hasInRange(self, *kw , **kwd):
    """Checks if coordinates are in the range of the matrix for this base_id
    """
    if getattr(aq_base(self), 'index', None) is None:
      return 0

    base_id = kwd.get('base_id', "cell")
    if not self.index.has_key(base_id):
      return 0
    base_item = self.index[base_id]
    for i, my_id in enumerate(kw):
      if not base_item.has_key(i) or not base_item[i].has_key(my_id):
        return 0

    return 1

  security.declareProtected( Permissions.ModifyPortalContent,
                             '_setCellRange' )
  def _setCellRange(self, *args, **kw):
    """Set a new range for a matrix

    Each value for each axis is assigned an integer id.
    If the number of axis changes, everything is reset.
    Otherwise, ids are never changed, so that cells never need to be renamed:
    this means no sort is garanteed, and there can be holes.
    """
    base_id = kw.get('base_id', 'cell')
    # Get (initialize if necessary) index for considered matrix (base_id).
    try:
      index = aq_base(self).index
    except AttributeError:
      index = self.index = PersistentMapping()
    to_delete = []
    try:
      index = index[base_id]
      if len(args) != len(index):
        # The number of axis changes so we'll delete all existing cells and
        # renumber everything from 1.
        to_delete = INFINITE_SET,
        index.clear()
    except KeyError:
      index[base_id] = index = PersistentMapping()
    # For each axis ...
    for i, axis in enumerate(args):
      # ... collect old axis keys and allocate ids for new ones.
      axis = set(axis)
      last_id = -1
      try:
        id_dict = index[i]
      except KeyError:
        index[i] = id_dict = PersistentMapping()
      else:
        delete = set()
        to_delete.append(delete)
        for k, v in id_dict.items():
          try:
            axis.remove(k)
            if last_id < v:
              last_id = v
          except KeyError:
            delete.add(v)
            del id_dict[k]
        # At this point, last_id contains the greatest id.
      for k in sorted(axis):
        last_id += 1
        id_dict[k] = last_id
    # Remove old cells if any.
    if any(to_delete):
      prefix = base_id + '_'
      prefix_len = len(prefix)
      for cell_id in list(self.objectIds()):
        if cell_id.startswith(prefix):
          for i, j in enumerate(cell_id[prefix_len:].split('_')):
            if int(j) in to_delete[i]:
              self._delObject(cell_id)
              break

  security.declareProtected( Permissions.ModifyPortalContent, 'setCellRange' )
  def setCellRange(self, *kw, **kwd):
    """Update the matrix ranges using provided lists of indexes (kw).
    """
    self._setCellRange(*kw, **kwd)
    self.reindexObject()

  security.declareProtected(Permissions.ModifyPortalContent,
                            '_updateCellRange')
  def _updateCellRange(self, base_id, **kw):
    """Update cell range based on asCellRange type based method.
    """
    script = self._getTypeBasedMethod('asCellRange', **kw)
    if script is None:
      raise UnboundLocalError,\
             "Did not find cell range script for portal type: %r" %\
             self.getPortalType()
    cell_range = script(base_id=base_id, matrixbox=0, **kw)
    self._setCellRange(base_id=base_id, *cell_range)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'updateCellRange')
  def updateCellRange(self, base_id='cell', **kw):
    """ same as _updateCellRange, but reindex the object. """
    self._updateCellRange(base_id=base_id, **kw)
    self.reindexObject()


  security.declareProtected( Permissions.ModifyPortalContent,
                             '_renameCellRange' )
  def _renameCellRange(self, *kw, **kwd):
    """Rename a range for a matrix, this method can also handle a change in
    the size of a matrix
    """
    base_id = kwd.get('base_id', 'cell')

    if getattr(aq_base(self), 'index', None) is None:
      self.index = PersistentMapping()

    # Return if previous range is the same
    current_range = self.getCellRange(base_id=base_id) or []
    if current_range == list(kw): # kw is a tuple
      LOG('XMLMatrix',0,'return form _setCellRange - no need to change range')
      return

    current_len = len(current_range)
    new_len = len(kw)
    len_delta = new_len - current_len

    # We must make sure the base_id exists
    # in the event of a matrix creation for example
    if not self.index.has_key(base_id):
      # Create an index for this base_id
      self.index[base_id] = PersistentMapping()

    cell_id_list = []
    for cell_id in self.getCellIdList(base_id = base_id):
      if self.get(cell_id) is not None:
        cell_id_list.append(cell_id)

    # First, delete all cells which are out of range.
    size_list = map(len, kw)
    if len_delta < 0:
      size_list.extend([1] * (-len_delta))
    def is_in_range(cell_id):
      for i, index in enumerate(cell_id[len(base_id)+1:].split('_')):
        if int(index) >= size_list[i]:
          self._delObject(cell_id)
          return False
      return True
    cell_id_list = filter(is_in_range, cell_id_list)

    # Secondly, rename coordinates. This does not change cell ids.
    for i in range(max(new_len, current_len)):
      if i >= new_len:
        del self.index[base_id][i]
      else:
        if i >= current_len:
          self.index[base_id][i] = PersistentMapping()
        for place in self.index[base_id][i].keys():
          if place not in kw[i]:
            del self.index[base_id][i][place]

        for j, place in enumerate(kw[i]):
          self.index[base_id][i][place] = j

    # Lastly, rename ids and catalog/uncatalog everything.
    if len_delta > 0:
      # Need to move, say, base_1_2 -> base_1_2_0
      appended_id = '_0' * len_delta
      for old_id in cell_id_list:
        cell = self.get(old_id)
        if cell is not None:
          new_id = old_id + appended_id
          self._delObject(old_id)
          cell.isIndexable = ConstantGetter('isIndexable', value=False)
          cell.id = new_id
          self._setObject(new_id, aq_base(cell))
          cell.isIndexable = ConstantGetter('isIndexable', value=True)
          cell.reindexObject()
          #cell.unindexObject(path='%s/%s' % (self.getUrl(), old_id))
    elif len_delta < 0:
      # Need to move, say, base_1_2_0 -> base_1_2
      removed_id_len = 2 * (-len_delta)
      for old_id in cell_id_list:
        cell = self.get(old_id)
        if cell is not None:
          new_id = old_id[:-removed_id_len]
          self._delObject(old_id)
          cell.isIndexable = ConstantGetter('isIndexable', value=False)
          cell.id = new_id
          self._setObject(new_id, aq_base(cell))
          cell.isIndexable = ConstantGetter('isIndexable', value=True)
          cell.reindexObject()
          #cell.unindexObject(path='%s/%s' % (self.getUrl(), old_id))

  security.declareProtected( Permissions.ModifyPortalContent,
                             'renameCellRange' )
  def renameCellRange(self, *kw, **kwd):
    """Update the matrix ranges using provided lists of indexes (kw).
    This keep cell values when dimensions are added or removed.
    """
    self._renameCellRange(*kw, **kwd)
    self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCellRange')
  def getCellRange(self, base_id='cell'):
    """
        Returns the cell range as a list of index ids
    """
    try:
      cell_range = aq_base(self).index[base_id]
    except (AttributeError, KeyError):
      return []
    return [x.keys() for _, x in sorted(cell_range.iteritems())]

  security.declareProtected( Permissions.ModifyPortalContent, 'newCell' )
  def newCell(self, *kw, **kwd):
    """
        This method creates a new cell
    """
    if getattr(aq_base(self), 'index', None) is None:
      return None
    base_id = kwd.get('base_id', "cell")
    if not self.index.has_key(base_id):
      return None

    cell_id = self.keyToId(kw, base_id = base_id)
    if cell_id is None:
      raise KeyError, 'Invalid key: %s' % str(kw)

    cell = self.get(cell_id)
    if cell is not None:
      return cell
    else:
      return self.newCellContent(cell_id,**kwd)

  security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
  def newCellContent(self, cell_id, portal_type=None, **kw):
    """Creates a new content as a cell.
    This method is meant to be overriden by subclasses.
    """
    if portal_type is None:
      for x in self.allowedContentTypes():
        portal_type_id = x.getId()
        if portal_type_id.endswith(' Cell'):
          portal_type = portal_type_id
          break

    return self.newContent(id=cell_id, portal_type=portal_type, **kw)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCellKeyList' )
  def getCellKeyList(self, base_id = 'cell'):
    """Returns a list of possible keys as tuples
    """
    if getattr(aq_base(self), 'index', None) is None:
      return ()
    if not self.index.has_key(base_id):
      return ()
    index = self.index[base_id]
    id_tuple = [v.keys() for v in index.itervalues()]
    if len(id_tuple) == 0:
      return ()
    return cartesianProduct(id_tuple)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCellKeys' )
  getCellKeys = getCellKeyList

  # We should differenciate in future existing tuples from possible tuples
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCellRangeKeyList' )
  getCellRangeKeyList = getCellKeyList

  security.declareProtected( Permissions.AccessContentsInformation, 'keyToId' )
  def keyToId(self, kw, base_id = 'cell'):
    """Converts a key into a cell id
    """
    index = self.index[base_id]
    cell_id_list = [base_id]
    append = cell_id_list.append
    for i, item in enumerate(kw):
      try:
        append(str(index[i][item]))
      except KeyError:
        return None
    return '_'.join(cell_id_list)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCellIdList' )
  def getCellIdList(self, base_id = 'cell'):
    """Returns a list of possible ids as tuples
    """
    if getattr(aq_base(self), 'index', None) is None:
      return ()
    if not self.index.has_key(base_id):
      return ()
    result = []
    append = result.append
    for kw in self.getCellKeys(base_id = base_id):
      cell_id = self.keyToId(kw, base_id = base_id )
      if cell_id is not None:
        append(cell_id)

    return result

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCellIds' )
  getCellIds = getCellIdList

  security.declareProtected( Permissions.AccessContentsInformation, 'cellIds' )
  cellIds = getCellIdList

  # We should differenciate in future all possible ids for existing ids
  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCellRangeIdList' )
  getCellRangeIdList = getCellIdList

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getCellValueList' )
  def getCellValueList(self, base_id = 'cell'):
    """Returns a list of cell values as tuples
    """
    result = []
    append = result.append
    for id in self.getCellIdList(base_id=base_id):
      o = self.get(id)
      if o is not None:
        append(o)
    return result

  security.declareProtected( Permissions.AccessContentsInformation,
                             'cellValues' )
  cellValues = getCellValueList

  security.declareProtected( Permissions.AccessContentsInformation,
                             'getMatrixList' )
  def getMatrixList(self):
    """Return possible base_id values
    """
    if getattr(aq_base(self), 'index', None) is None:
      return ()
    return self.index.keys()

  security.declareProtected( Permissions.ModifyPortalContent, 'delMatrix' )
  def delMatrix(self, base_id = 'cell'):
    """Delete all cells for a given base_id

      XXX BAD NAME: make a difference between deleting matrix and matrix cells
    """
    ids = self.getCellIds(base_id = base_id)
    my_ids = []
    append = my_ids.append
    for i in self.objectIds():
      if i in ids:
        append(i)

    if len(my_ids) > 0:
      self.manage_delObjects(ids=my_ids)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'delCells' )
  delCells = delMatrix

  security.declareProtected( Permissions.AccessContentsInformation,
                             '_checkConsistency' )
  def _checkConsistency(self, fixit=0):
    """Constraint API.
    """
    # Check useless cells
    to_delete_set = set()
    error_list = []
    def addError(error_message):
      if fixit:
        error_message += ' (fixed)'
      error = (self.getRelativeUrl(),
               'XMLMatrix inconsistency',
               102,
               error_message)

      error_list.append(error)

    # We make sure first that there is an index
    if getattr(aq_base(self), 'index', None) is None:
      self.index = PersistentMapping()
    # We will check each cell of the matrix the matrix

    # XXX This code assumes the following predicate:
    #   each subobject of an XMLMatrix is either a Cell that needs
    #   consistency checking OR ( is not a Cell, and has an id that is
    #   not like "(\w+_)+(\d+_)*\d+" )
    # But Documents inheriting XMLMatrix can have unrelated, non-cell
    # subobjects, possibly with id looking like some_id_2. If it ever happens,
    # an error will be wrongly raised.
    for obj in self.objectValues():
      object_id = obj.getId()
      # obect_id is equal to something like 'something_quantity_3_2'
      # So we need to check for every object.id if the value
      # looks like good or not. We split the name
      # check each key in index
      # First we make sure this is a cell
      object_id_split = object_id.split('_')

      base_id = None
      cell_coordinate_list = []
      while object_id_split:
        coordinate = None
        try:
          coordinate = int(object_id_split[-1])
        except ValueError:
          # The last item is not a coordinate, object_id_split hence
          # only contains the base_id elements
          base_id = '_'.join(object_id_split)
          break
        else:
          cell_coordinate_list.insert(0, coordinate)
          # the last item is a coordinate not part of base_id
          object_id_split.pop()

      current_dimension = len(cell_coordinate_list)
      if current_dimension > 0 and base_id is not None:
        if not self.index.has_key(base_id):
          # The matrix does not have this base_id
          addError("There is no index for base_id %s" % base_id)
          to_delete_set.add(object_id)
          continue

        # Check empty indices.
        empty_list = []
        base_item = self.index[base_id]
        for key, value in base_item.iteritems():
          if value is None or len(value) == 0:
            addError("There is no id for the %dth axis of base_id %s" % (key, base_id))
            empty_list.append(key)
        if fixit:
          for i in empty_list:
            del base_item[key]

        len_id = len(base_item)
        if current_dimension != len_id:
          addError("Dimension of cell is %s but should be %s" % (current_dimension,
                                                                 len_id))
          to_delete_set.add(object_id)
        else :
          for i, coordinate in enumerate(cell_coordinate_list):
            if coordinate not in base_item[i].values():
              addError("Cell %s is out of bound" % object_id)
              to_delete_set.add(object_id)
              break

    if fixit and len(to_delete_set) > 0:
      self.manage_delObjects(list(to_delete_set))

    return error_list

  security.declareProtected( Permissions.ModifyPortalContent, 'notifyAfterUpdateRelatedContent' )
  def notifyAfterUpdateRelatedContent(self, previous_category_url, new_category_url):
    """Hook called when a category is renamed.

      We must do some matrix range update in the event matrix range
      is defined by a category
    """
    LOG('XMLMatrix notifyAfterUpdateRelatedContent', 0, str(new_category_url))
    update_method = self.portal_categories.updateRelatedCategory
    for base_id in self.getMatrixList():
      cell_range = self.getCellRange(base_id=base_id)
      new_cell_range = []
      for range_item_list in cell_range:
        new_range_item_list = map(lambda c: update_method(c, previous_category_url, new_category_url), range_item_list)
        new_cell_range.append(new_range_item_list)
      kwd = {'base_id': base_id}
      LOG('XMLMatrix notifyAfterUpdateRelatedContent matrix', 0, str(base_id))
      LOG('XMLMatrix notifyAfterUpdateRelatedContent _renameCellRange', 0, str(new_cell_range))
      self._renameCellRange(*new_cell_range,**kwd)

InitializeClass(Matrix)
