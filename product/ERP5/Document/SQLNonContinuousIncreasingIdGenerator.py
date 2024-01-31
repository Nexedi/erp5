##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Daniele Vanbaelinghem <daniele@nexedi.com>
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

import six
from Products.ERP5Type.Utils import ensure_list

import zope.interface
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Utils import ScalarMaxConflictResolver
from Products.ERP5.Document.IdGenerator import IdGenerator
from MySQLdb import ProgrammingError
from MySQLdb.constants.ER import NO_SUCH_TABLE
from zLOG import LOG, INFO
from BTrees.OOBTree import OOBTree

@zope.interface.implementer(interfaces.IIdGenerator)
class SQLNonContinuousIncreasingIdGenerator(IdGenerator):
  """
    Generate some ids with mysql storage and also zodb is enabled
    by the checkbox : StoredInZodb
  """
  # CMF Type Definition
  meta_type = 'ERP5 SQL Non Continous Increasing Id Generator'
  portal_type = 'SQL Non Continous Increasing Id Generator'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative property
  property_sheets = (PropertySheet.SQLIdGenerator,
                    ) + IdGenerator.property_sheets

  last_max_id_dict = None

  def _generateNewId(self, id_group, id_count=1, default=None, poison=False):
    """
      Return the next_id with the last_id with the sql method
      Store the last id on a database in the portal_ids table
      If stored in zodb is enable, to store the last id use
      ScalarMaxConflictResolver inspired by BTrees.Length to manage
      conflict in the zodb, use also a persistant
      mapping to be persistent
    """
    # Check the arguments
    if id_group in (None, 'None'):
      raise ValueError('%r is not a valid group Id.' % id_group)
    if not isinstance(id_group, str):
      raise TypeError('id_group must be str')
    if default is None:
      default = 0

    if self.getStoredInZodb():
      # Make sure 'last_max_id_dict' is initialized before we generate a new id,
      # to avoid issues in case of upgrade.
      last_max_id_dict = self.last_max_id_dict
      if last_max_id_dict is None:
        # If the dictionary not exist, initialize the generator
        self.initializeGenerator()
        last_max_id_dict = self.last_max_id_dict
    else:
      last_max_id_dict = None

    # Retrieve the zsql method
    portal = self.getPortalObject()
    result_query = portal.IdTool_zGenerateId(id_group=id_group,
                                             id_count=id_count,
                                             default=default)
    try:
      # Tries of generate the new_id
      new_id = result_query[0]['LAST_INSERT_ID()']
      if poison:
        portal.IdTool_zSetLastId(id_group, None)
      # Commit the changement of new_id
      portal.IdTool_zCommit()
    except ProgrammingError as error:
      if error[0] != NO_SUCH_TABLE:
        raise

    if last_max_id_dict is not None:
      # Store the new_id on ZODB if the checkbox storedInZodb is enabled
      last_max_id = last_max_id_dict.get(id_group)
      if last_max_id is None:
        last_max_id_dict[id_group] = ScalarMaxConflictResolver(new_id)
      else:
        last_max_id_value = last_max_id.value
        if new_id <= last_max_id_value:
          raise ValueError('The last id %s stored in ZODB dictionary is higher'
                           ' than the new id %s generated for id_group %r.'
                           ' Invoke %s/rebuildSqlTable to fix this problem.'
                           % (last_max_id_value, new_id, id_group,
                              self.absolute_url()))
        # Check the store interval to store the data
        if last_max_id_value <= new_id - (self.getStoreInterval() or 1):
          last_max_id.set(new_id)
        if poison:
          last_max_id.set(None)
    return new_id

  def _updateSqlTable(self):
    """
      Update the portal ids table with the data of persistent dictionary
    """
    portal = self.getPortalObject()
    set_last_id_method = portal.IdTool_zSetLastId
    id_group_done = []
    # Save the last id of persistent dict if it is higher that
    # the last id stored in the sql table
    for line in self._getValueListFromTable():
      id_group = line['id_group']
      assert isinstance(id_group, str)
      last_id = line['last_id']
      if id_group in self.last_max_id_dict and \
        self.last_max_id_dict[id_group].value > last_id:
        set_last_id_method(id_group=id_group,
            last_id=self.last_max_id_dict[id_group].value)
      id_group_done.append(id_group)

    # save the last ids which not exist in sql
    for id_group in set(self.last_max_id_dict).difference(id_group_done):
      set_last_id_method(id_group=id_group,
          last_id=self.last_max_id_dict[id_group].value)

  security.declareProtected(Permissions.AccessContentsInformation,
      'generateNewId')
  def generateNewId(self, id_group=None, default=None, poison=False):
    """
      Generate the next id in the sequence of ids of a particular group
    """
    return self._generateNewId(id_group=id_group, default=default, poison=poison)

  security.declareProtected(Permissions.AccessContentsInformation,
      'generateNewIdList')
  def generateNewIdList(self, id_group=None, id_count=1, default=None, poison=False):
    """
      Generate a list of next ids in the sequence of ids of a particular group
    """
    new_id = 1 + self._generateNewId(id_group=id_group, id_count=id_count,
                                     default=default, poison=poison)
    return ensure_list(range(new_id - id_count, new_id))

  security.declareProtected(Permissions.ModifyPortalContent,
      'initializeGenerator')
  def initializeGenerator(self):
    """
      Initialize generator. This is mostly used when a new ERP5 site
      is created. Some generators will need to do some initialization like
      prepare some data in ZODB
    """
    LOG('initialize SQL Generator', INFO, 'Id Generator: %s' % (self,))
    # Check the dictionnary
    if self.last_max_id_dict is None:
      self.last_max_id_dict = OOBTree()
    # Create table portal_ids if not exists
    portal = self.getPortalObject()
    try:
      portal.IdTool_zGetValueList()
    except ProgrammingError as error:
      if error[0] != NO_SUCH_TABLE:
        raise
      portal.IdTool_zDropTable()
      portal.IdTool_zCreateEmptyTable()

    # XXX compatiblity code below, dump the old dictionnaries
    # Retrieve the zsql_method
    portal_ids = portal.portal_ids
    get_last_id_method = portal.IdTool_zGetLastId
    set_last_id_method = portal.IdTool_zSetLastId
    storage = self.getStoredInZodb()
    # Recovery last_max_id_dict datas in zodb if enabled and is in mysql
    if not (self.last_max_id_dict or
            getattr(portal_ids, 'dict_length_ids', None) is None):
      dump_dict = portal_ids.dict_length_ids
      for id_group, last_id in dump_dict.items():
        assert isinstance(id_group, str)
        last_insert_id = get_last_id_method(id_group=id_group)
        last_id = int(last_id.value)
        if len(last_insert_id) != 0:
          last_insert_id = last_insert_id[0]['LAST_INSERT_ID()']
          if last_insert_id >= last_id:
            if storage:
              self.last_max_id_dict[id_group] = ScalarMaxConflictResolver(last_insert_id)
            continue
        set_last_id_method(id_group=id_group, last_id=last_id)
        if storage:
          self.last_max_id_dict[id_group] = ScalarMaxConflictResolver(last_id)

    # Store last_max_id_dict in mysql
    if storage:
      self._updateSqlTable()

  security.declareProtected(Permissions.ModifyPortalContent,
      'clearGenerator')
  def clearGenerator(self):
    """
      Clear generators data. This can be usefull when working on a
      development instance or in some other rare cases. This will
      loose data and must be use with caution

      This can be incompatible with some particular generator implementation,
      in this case a particular error will be raised (to be determined and
      added here)
    """
    # Remove dictionary
    self.last_max_id_dict = OOBTree()
    # Remove and recreate portal_ids table
    portal = self.getPortalObject()
    portal.IdTool_zDropTable()
    portal.IdTool_zCreateEmptyTable()

  security.declareProtected(Permissions.ModifyPortalContent,
      'exportGeneratorIdDict')
  def exportGeneratorIdDict(self):
    """
      Export last id values in a dictionnary in the form { group_id : last_id }
    """
    portal = self.getPortalObject()
    # Store last_max_id_dict in mysql
    if self.getStoredInZodb():
      self._updateSqlTable()
    # Return values from sql
    return {line['id_group']: int(line['last_id'])
            for line in self._getValueListFromTable()}

  security.declareProtected(Permissions.ModifyPortalContent,
      'importGeneratorIdDict')
  def importGeneratorIdDict(self, id_dict=None, clear=False):
    """
      Import data, this is usefull if we want to replace a generator by
      another one.
    """
    if clear:
      self.clearGenerator()
    portal = self.getPortalObject()
    set_last_id_method = portal.IdTool_zSetLastId
    if not isinstance(id_dict, dict):
      raise TypeError('the argument given is not a dictionary')
    new_id_dict = {}
    for key, value in id_dict.items():
      if isinstance(value, int):
        set_last_id_method(id_group=key, last_id=value)
        # The id must be a ScalarMaxConflictResolver object for the persistent dict
        new_id_dict[key] = ScalarMaxConflictResolver(value)
      else:
        raise TypeError('the value in the dictionary given is not a integer')
    # Update persistent dict
    if self.getStoredInZodb():
      if self.last_max_id_dict is None:
        self.last_max_id_dict = OOBTree()
      self.last_max_id_dict.update(new_id_dict)

  security.declareProtected(Permissions.ModifyPortalContent,
       'rebuildGeneratorIdDict')
  def rebuildGeneratorIdDict(self):
    """
      Rebuild generator id dict from SQL table.

      This is usefull when we are migrating the dict structure, or cleanly
      rebuild the dict from sql table. This method is opposite of
      rebuildSqlTable().
    """
    if not self.getStoredInZodb():
      raise RuntimeError('Please set \"stored in zodb\" flag before rebuild.')
    id_dict = self.exportGeneratorIdDict()
    self.importGeneratorIdDict(id_dict=id_dict, clear=True)

  security.declareProtected(Permissions.ModifyPortalContent,
      'rebuildSqlTable')
  def rebuildSqlTable(self):
    """
      After a mysql crash, it could be needed to restore values stored in
      zodb into mysql

      TODO : take into account the case where the value is stored every X
             generation
    """
    portal = self.getPortalObject()
    portal.IdTool_zDropTable()
    portal.IdTool_zCreateEmptyTable()
    self._updateSqlTable()

  def _getValueListFromTable(self):
    """
      get all the records of portal_ids table
      returns list of id_dict. like [{'id_group', 'last_id'},..]

      TODO: This method which is used in _updateSqlTable() still is not
      scalable when portal_ids has a large amount of records.
      If split into several transaction is acceptable, you can scale
      it like updateLastMaxIdDictFromTable() do with the id_group parameter.
    """
    portal = self.getPortalObject()
    value_dict_list = []
    id_group = None
    while True:
      record_list = portal.IdTool_zGetValueList(
                       id_group=id_group).dictionaries()
      value_dict_list.extend(record_list)
      if record_list:
        id_group = record_list[-1]['id_group']
      else:
        break
    return value_dict_list

  security.declareProtected(Permissions.ModifyPortalContent,
       'updateLastMaxIdDictFromTable')
  def updateLastMaxIdDictFromTable(self, id_group=None):
    """
      Update the Persistent id_dict from portal_ids table
      in steps of the max_rows quantity of IdTool_getValueList ZSQL Method.
      The quantity is currently configured 1000. This means update 1000
      keys as the max in one call.
      Returns the last id_group value that is updated in the call.

    -- id_group: update the id_dict from this value by alphabetial sort
    """
    portal = self.getPortalObject()
    last_max_id_dict = self.last_max_id_dict
    if last_max_id_dict is None:
      self.last_max_id_dict = last_max_id_dict = OOBTree()
    last_id_group = None
    for line in portal.IdTool_zGetValueList(id_group=id_group):
      last_id_group = id_group = line[0]
      last_id = line[1]
      try:
        scalar = last_max_id_dict[id_group]
      except KeyError:
        last_max_id_dict[id_group] = ScalarMaxConflictResolver(last_id)
      else:
        scalar.set(last_id)
    return last_id_group
