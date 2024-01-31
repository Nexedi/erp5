# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Globals import PersistentMapping
from Products.ERP5Type.Utils import ScalarMaxConflictResolver
from BTrees.Length import Length
from BTrees.OOBTree import OOBTree
from six.moves import range
import six


class TestIdToolUpgrade(ERP5TypeTestCase):
  """
  Automatic upgrade of id tool is really sensible to any change. Therefore,
  make sure that the upgrade is still working even if there changes.

  specific test is used, because here some really nasty things are done
  """

  def getTitle(self):
    """
      Return the title of test
    """
    return "Test Id Tool Upgrade"

  def afterSetUp(self):
    self.login()
    self.id_tool = self.portal.portal_ids
    self.id_tool.initializeGenerator(all=True)
    self.createGenerators()
    self.tic()

  def beforeTearDown(self):
    self.portal.portal_caches.clearAllCache()
    self.id_tool.clearGenerator(all=True)
    self.tic()

  def createGenerators(self):
    """
      Initialize some generators for the tests
    """
    self.application_sql_generator = self.id_tool.newContent(\
                            portal_type='Application Id Generator',
                            reference='test_application_sql',
                            version='001')
    self.conceptual_sql_generator = self.id_tool.newContent(\
                           portal_type='Conceptual Id Generator',
                           reference='test_non_continuous_increasing',
                           version='001')
    self.sql_generator = self.id_tool.newContent(\
                    portal_type='SQL Non Continuous Increasing Id Generator',
                    reference='test_sql_non_continuous_increasing',
                    version='001')
    self.application_sql_generator.setSpecialiseValue(\
                                   self.conceptual_sql_generator)
    self.conceptual_sql_generator.setSpecialiseValue(self.sql_generator)

    self.application_zodb_generator = self.id_tool.newContent(\
                            portal_type='Application Id Generator',
                            reference='test_application_zodb',
                            version='001')
    self.conceptual_zodb_generator = self.id_tool.newContent(\
                           portal_type='Conceptual Id Generator',
                           reference='test_continuous_increasing',
                           version='001')
    self.zodb_generator = self.id_tool.newContent(\
                    portal_type='ZODB Continuous Increasing Id Generator',
                    reference='test_zodb_continuous_increasing',
                    version='001')
    self.application_zodb_generator.setSpecialiseValue(\
                                    self.conceptual_zodb_generator)
    self.conceptual_zodb_generator.setSpecialiseValue(self.zodb_generator)

  def getLastGenerator(self, id_generator):
    """
      Return Last Id Generator
    """
    document_generator = self.id_tool.searchFolder(reference=id_generator)[0]
    application_generator = document_generator.getLatestVersionValue()
    conceptual_generator = application_generator.getSpecialiseValue()\
                           .getLatestVersionValue()
    last_generator = conceptual_generator.getSpecialiseValue()\
                     .getLatestVersionValue()
    return last_generator

  def testUpgradeIdToolDicts(self):
    # With old erp5_core, we have no generators, no IdTool_* zsql methods,
    # and we have a dictionary stored on id tool
    id_tool = self.portal.portal_ids
    # Rebuild a persistent mapping like it already existed in beginning 2010
    # First persistent mapping of generateNewLengthIdList
    id_tool.dict_length_ids = PersistentMapping()
    id_tool.dict_length_ids['foo'] = Length(5)
    id_tool.dict_length_ids['bar'] = Length(5)
    id_tool.IdTool_zSetLastId(id_group='foo', last_id=5)
    id_tool.IdTool_zSetLastId(id_group='bar', last_id=10)
    # Then persistent mapping of generateNewId
    id_tool.dict_ids = PersistentMapping()
    id_tool.dict_ids['foo'] = 3
    # it was unfortunately possible to define something else
    # than strings
    id_tool.dict_ids[('bar','baz')] = 2
    # Delete portal type info and new generators
    id_tool.manage_delObjects(ids=list(id_tool.objectIds()))
    id_tool.__class__.getTypeInfo = lambda self: None
    # Test with compatibility
    self.tic()
    id_list = id_tool.generateNewLengthIdList(id_group='foo', store=1)
    self.assertEqual(id_list, [5])
    self.assertEqual(int(id_tool.dict_length_ids['foo'].value), 6)
    # Now, restore and make sure we can still generate ids
    del id_tool.__class__.getTypeInfo
    bt = self.portal.portal_templates.getInstalledBusinessTemplate('erp5_core',
                                                                  strict=True)
    for path, obj in six.iteritems(bt._path_item._objects):
      path, obj_id = path.rsplit('/', 1)
      if path == 'portal_ids':
        id_tool._setObject(obj_id, obj._getCopy(bt))
    self.tic()
    id_list = id_tool.generateNewLengthIdList(id_group='foo')
    # it is known that with current upgrade there is a hole
    self.assertEqual(id_list, [7])
    new_id = id_tool.generateNewId(id_group='foo')
    self.assertEqual(new_id, 4)
    new_id = id_tool.generateNewId(id_group=('bar','baz'))
    self.assertEqual(new_id, 3)
    # Make sure that the old code is not used any more, so the dic on
    # id tool should not change, checking for length_dict
    self.assertEqual(int(id_tool.dict_length_ids['foo'].value), 6)
    id_list = id_tool.generateNewLengthIdList(id_group='bar')
    self.assertEqual(id_list, [11])
    generator_list = [x for x in id_tool.objectValues()
                      if x.getReference()=='mysql_non_continuous_increasing']
    self.assertEqual(len(generator_list), 1)
    generator = generator_list[0]
    self.assertEqual(generator.last_max_id_dict['foo'].value, 7)
    self.assertEqual(generator.last_max_id_dict['bar'].value, 11)
    # Make sure that the old code is not used any more, so the dic on
    # id tool should not change, checking for dict
    self.assertEqual(id_tool.dict_ids['foo'], 3)
    generator_list = [x for x in id_tool.objectValues()
                      if x.getReference()=='zodb_continuous_increasing']
    self.assertEqual(len(generator_list), 1)
    generator = generator_list[0]
    self.assertEqual(generator.last_id_dict['foo'], 4)
    self.assertEqual(generator.last_id_dict["('bar', 'baz')"], 3)


  def _setUpLastMaxIdDict(self, id_generator_reference):
    def countup(id_generator, id_group, until):
      for _ in range(until + 1):
        self.id_tool.generateNewId(id_generator=id_generator_reference,
                                   id_group=id_group)

    countup(id_generator_reference, 'A-01', 2)
    countup(id_generator_reference, 'B-01', 1)
    var_id = 'C-%04d'
    for x in range(self.a_lot_of_key):
      countup(id_generator_reference, var_id % x, 0)

  def _getLastIdDictName(self, id_generator):
    portal_type = id_generator.getPortalType()
    if portal_type == 'SQL Non Continuous Increasing Id Generator':
      return 'last_max_id_dict'
    elif portal_type == 'ZODB Continuous Increasing Id Generator':
      return 'last_id_dict'
    else:
      raise RuntimeError("not expected to test the generator :%s" % portal_type)

  def _getLastIdDict(self, id_generator):
    last_id_dict_name = self._getLastIdDictName(id_generator)
    return getattr(id_generator, last_id_dict_name)

  def _setLastIdDict(self, id_generator, value):
    last_id_dict_name = self._getLastIdDictName(id_generator)
    setattr(id_generator, last_id_dict_name, value)

  def _getValueFromLastIdDict(self, last_id_dict, key):
    value = last_id_dict[key]
    if isinstance(value, int):
      # in ZODB Id Generator it is stored in int
      return value
    elif isinstance(value, ScalarMaxConflictResolver):
      return value.value
    else:
      raise RuntimeError('not expected to test the value: %s' % value)

  def _assertIdGeneratorLastMaxIdDict(self, id_generator):
    last_id_dict = self._getLastIdDict(id_generator)
    self.assertEqual(2, self._getValueFromLastIdDict(last_id_dict, 'A-01'))
    self.assertEqual(1, self._getValueFromLastIdDict(last_id_dict, 'B-01'))
    for x in range(self.a_lot_of_key):
      key = 'C-%04d' % x
      self.assertEqual(0, self._getValueFromLastIdDict(last_id_dict, key))

    # 1(A-01) + 1(B-01) + a_lot_of_key(C-*)
    number_of_group_id = self.a_lot_of_key + 2
    self.assertEqual(number_of_group_id,
                     len(id_generator.exportGeneratorIdDict()))
    self.assertEqual(number_of_group_id, len(last_id_dict))


  def _checkDataStructureMigration(self, id_generator):
    """ First, simulate previous data structure which is using
    PersisntentMapping as the storage, then migrate to OOBTree.
    Then, migrate the id generator again from OOBTree to OOBtree
    just to be sure."""
    id_generator_reference  = id_generator.getReference()

    reference_portal_type_dict = {
      'test_sql_non_continuous_increasing':'SQL Non Continuous ' \
                                           'Increasing Id Generator',
      'test_zodb_continuous_increasing':'ZODB Continuous ' \
                                        'Increasing Id Generator'
    }
    try:
      portal_type = reference_portal_type_dict[id_generator_reference]
      self.assertEqual(id_generator.getPortalType(), portal_type)
    except:
      raise ValueError("reference is not valid: %s" % id_generator_reference)

    self._setLastIdDict(id_generator, PersistentMapping()) # simulate previous
    last_id_dict = self._getLastIdDict(id_generator)

    # setUp the data for migration test
    self._setUpLastMaxIdDict(id_generator_reference)

    # test migration: PersistentMapping to OOBTree
    self.assertIsInstance(last_id_dict, PersistentMapping)
    self._assertIdGeneratorLastMaxIdDict(id_generator)
    id_generator.rebuildGeneratorIdDict() # migrate the dict
    self._assertIdGeneratorLastMaxIdDict(id_generator)

    # test migration: OOBTree to OOBTree. this changes nothing, just to be sure
    last_id_dict = self._getLastIdDict(id_generator)
    self.assertIsInstance(last_id_dict, OOBTree)
    self._assertIdGeneratorLastMaxIdDict(id_generator)
    id_generator.rebuildGeneratorIdDict() # migrate the dict
    self._assertIdGeneratorLastMaxIdDict(id_generator)

    # test migration: SQL to OOBTree
    if id_generator.getPortalType() == \
      'SQL Non Continuous Increasing Id Generator':
      self._setLastIdDict(id_generator, OOBTree()) # set empty one
      last_id_dict = self._getLastIdDict(id_generator)
      self.assertEqual(len(last_id_dict), 0) # 0 because it is empty
      self.assertIsInstance(last_id_dict, OOBTree)
      # migrate the dict totally from sql table in this case
      id_generator.rebuildGeneratorIdDict()
      self._assertIdGeneratorLastMaxIdDict(id_generator)


  def testRebuildIdDictFromPersistentMappingToOOBTree(self):
    """
      Check migration is working
    """
    # this is the amount of keys that is creating in this test
    self.a_lot_of_key = 1010
    # check sql id generator migration
    id_generator_reference = 'test_application_sql'
    id_generator = self.getLastGenerator(id_generator_reference)
    id_generator.setStoredInZodb(True)
    id_generator.clearGenerator() # clear stored data
    self._checkDataStructureMigration(id_generator)

    # check zodb id generator migration
    id_generator_reference = 'test_application_zodb'
    id_generator = self.getLastGenerator(id_generator_reference)
    id_generator.clearGenerator() # clear stored data
    self._checkDataStructureMigration(id_generator)

  def test_portal_ids_table_id_group_column_binary(self):
    """portal_ids.id_group is now created as VARCHAR,
    but it use to be binary. There is no data migration, the
    SQL method has been adjusted to cast during select.
    This checks that id generator works well when the column
    is VARBINARY, like it's the case for old instances.
    """
    self.assertEqual(
      self.sql_generator.generateNewId(id_group=self.id()),
      0)
    exported = self.sql_generator.exportGeneratorIdDict()
    self.tic()
    self.portal.portal_ids.IdTool_zCommit()

    self.portal.erp5_sql_connection.manage_test(
      'ALTER TABLE portal_ids MODIFY COLUMN id_group VARBINARY(255)'
    )
    self.tic()
    self.sql_generator.importGeneratorIdDict(exported, clear=True)
    self.tic()
    self.assertEqual(
      self.sql_generator.generateNewId(id_group=self.id()),
      1)
