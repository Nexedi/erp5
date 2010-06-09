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

import zope.interface
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.Utils import ScalarMaxConflictResolver
from Products.ERP5.Document.IdGenerator import IdGenerator
from _mysql_exceptions import ProgrammingError
from MySQLdb.constants.ER import NO_SUCH_TABLE
from zLOG import LOG, INFO

class SQLNonContinuousIncreasingIdGenerator(IdGenerator):
  """
    Generate some ids with mysql storage and also zodb is enabled
    by the checkbox : StoredInZodb
  """
  zope.interface.implements(interfaces.IIdGenerator)
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

  def _generateNewId(self, id_group, id_count=1, default=None):
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
      raise ValueError, '%s is not a valid group Id.' % (repr(id_group), )
    if default is None:
      default = 0

    # Retrieve the zsql method
    portal = self.getPortalObject()
    generate_id_method = getattr(portal, 'IdTool_zGenerateId', None)
    commit_method = getattr(portal, 'IdTool_zCommit', None)
    get_last_id_method = getattr(portal, 'IdTool_zGetLastId', None)
    if None in (generate_id_method, commit_method, get_last_id_method):
      raise AttributeError, 'Error while generating Id: ' \
        'idTool_zGenerateId and/or IdTool_zCommit and/or idTool_zGetLastId' \
        'could not be found.'
    result_query = generate_id_method(id_group=id_group, id_count=id_count, \
        default=default)
    try:
      # Tries of generate the new_id
      new_id = result_query[0]['LAST_INSERT_ID()']
      # Commit the changement of new_id
      commit_method()
    except ProgrammingError, error:
      if error[0] != NO_SUCH_TABLE:
        raise
      # If the database not exist, initialise the generator
      self.initializeGenerator()
    if self.getStoredInZodb():
      # Store the new_id on ZODB if the checkbox storedInZodb is enabled
      last_max_id_dict = getattr(aq_base(self), \
           'last_max_id_dict', None)
      if last_max_id_dict is None:
        # If the dictionary not exist, initialize the generator
        self.initializeGenerator()
        last_max_id_dict = getattr(aq_base(self), 'last_max_id_dict')
      # Store the new value id
      if last_max_id_dict.get(id_group, None) is None:
        last_max_id_dict[id_group] = ScalarMaxConflictResolver(new_id)
      last_max_id_dict[id_group].set(new_id)
    return new_id

  security.declareProtected(Permissions.AccessContentsInformation,
      'generateNewId')
  def generateNewId(self, id_group=None, default=None):
    """
      Generate the next id in the sequence of ids of a particular group
    """
    new_id = self._generateNewId(id_group=id_group, default=default)
    return new_id

  security.declareProtected(Permissions.AccessContentsInformation,
      'generateNewIdList')
  def generateNewIdList(self, id_group=None, id_count=1, default=None):
    """
      Generate a list of next ids in the sequence of ids of a particular group
    """
    new_id = self._generateNewId(id_group=id_group, id_count=id_count, \
                            default=default)
    return range(new_id - id_count + 1, new_id + 1)

  security.declareProtected(Permissions.AccessContentsInformation,
      'initializeGenerator')
  def initializeGenerator(self):
    """
      Initialize generator. This is mostly used when a new ERP5 site
      is created. Some generators will need to do some initialization like
      prepare some data in ZODB
    """
    LOG('initialize SQL Generator', INFO, 'Id Generator: %s' % (self,))
    # Check the dictionnary
    if getattr(self, 'last_max_id_dict', None) is None:
      self.last_max_id_dict = PersistentMapping()
    # Create table portal_ids if not exists
    portal = self.getPortalObject()
    get_value_list = getattr(portal, 'IdTool_zGetValueList', None)
    if get_value_list is None:
      raise AttributeError, 'Error while initialize generator:' \
        'idTool_zGetValueList could not be found.'
    try:
      get_value_list()
    except ProgrammingError, error:
      if error[0] != NO_SUCH_TABLE:
        raise
      drop_method = getattr(portal, 'IdTool_zDropTable', None)
      create_method = getattr(portal, 'IdTool_zCreateEmptyTable', None)
      if None in (drop_method, create_method):
        raise AttributeError, 'Error while initialize generator: ' \
          'idTool_zDropTable and/or idTool_zCreateTable could not be found.'
      drop_method()
      create_method()

    # XXX compatiblity code below, dump the old dictionnaries
    # Retrieve the zsql_method
    portal_ids = getattr(self, 'portal_ids', None)
    get_last_id_method = getattr(portal, 'IdTool_zGetLastId', None)
    set_last_id_method = getattr(portal, 'IdTool_zSetLastId', None)
    if None in (get_last_id_method, set_last_id_method):
      raise AttributeError, 'Error while generating Id: ' \
        'idTool_zGetLastId and/or idTool_zSetLastId could not be found.'
    storage = self.getStoredInZodb()
    # Recovery last_max_id_dict datas in zodb if enabled and is in mysql
    if len(self.last_max_id_dict) == 0 and \
      getattr(portal_ids, 'dict_length_ids', None) is not None:
      dump_dict = portal_ids.dict_length_ids
      for id_group, last_id in dump_dict.items():
        last_insert_id = get_last_id_method(id_group=id_group)
        if len(last_insert_id) != 0:
          last_insert_id = last_insert_id[0]['LAST_INSERT_ID()']
          if last_insert_id > last_id.value:
            # Check value in dict
            if storage and (not self.last_max_id_dict.has_key(id_group) or \
                self.last_max_id_dict[id_group].value < last_insert_id):
              self.last_max_id_dict[id_group] = ScalarMaxConflictResolver(last_insert_id)
              self.last_max_id_dict[id_group].set(last_insert_id)
            continue
        last_id = int(last_id.value)
        set_last_id_method(id_group=id_group, last_id=last_id)
        if storage:
          self.last_max_id_dict[id_group] = ScalarMaxConflictResolver(last_id)
          self.last_max_id_dict[id_group].set(last_id)

  security.declareProtected(Permissions.AccessContentsInformation,
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
    self.last_max_id_dict = PersistentMapping()
    # Remove and recreate portal_ids table
    portal = self.getPortalObject()
    drop_method = getattr(portal, 'IdTool_zDropTable', None)
    create_method = getattr(portal, 'IdTool_zCreateEmptyTable', None)
    if None in (drop_method, create_method):
      raise AttributeError, 'Error while clear generator: ' \
        'idTool_zDropTable and/or idTool_zCreateTable could not be found.'
    drop_method()
    create_method()

  security.declareProtected(Permissions.AccessContentsInformation,
      'rebuildSqlTable')
  def rebuildSqlTable(self):
    """
      After a mysql crash, it could be needed to restore values stored in
      zodb into mysql

      TODO : take into account the case where the value is stored every X
             generation 
    """
    portal = self.getPortalObject()
    getattr(portal, 'IdTool_zDropTable')()
    getattr(self, 'SQLNonContinuousIncreasingIdGenerator_zCreateTable')()

  security.declareProtected(Permissions.AccessContentsInformation,
      'rebuildSqlTable')
  def getPersistentIdDict(self):
    """
      Return all data stored in zodb
    """
    return dict([(x[0],x[1].value) for x in
       getattr(self, 'last_max_id_dict', {}).iteritems()])
