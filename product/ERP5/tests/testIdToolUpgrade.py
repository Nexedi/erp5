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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Globals import PersistentMapping
from BTrees.Length import Length
from zLOG import LOG

class TestIdTool(ERP5TypeTestCase):
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

  def testUpgradeIdToolDicts(self):
    # With old erp5_core, we have no generators, no IdTool_* zsql methods,
    # and we have a dictionary stored on id tool
    id_tool = self.getPortal().portal_ids
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
    # Delete new zsql methods which are used by new code
    skin_folder = self.getPortal().portal_skins.erp5_core
    custom_skin_folder = self.getPortal().portal_skins.custom
    script_id_list = [x for x in skin_folder.objectIds() 
                      if x.startswith('IdTool')]
    self.assertTrue(len(script_id_list)>0)
    cp_data = skin_folder.manage_cutObjects(ids=script_id_list)
    custom_skin_folder.manage_pasteObjects(cp_data)
    # Set old revision for erp5_core bt, because the id tool decide which code
    # to run depending on this revision
    template_tool = self.getPortal().portal_templates
    erp5_core_bt_list = [x for x in template_tool.objectValues()
                         if x.getTitle()=='erp5_core']
    self.assertEquals(len(erp5_core_bt_list), 1)
    erp5_core_bt = erp5_core_bt_list[0]
    erp5_core_bt.setRevision(1561)
    # Delete all new generators
    generator_id_list = [x for x in id_tool.objectIds()]
    id_tool.manage_delObjects(ids=generator_id_list)
    id_list = id_tool.generateNewLengthIdList(id_group='foo', store=1)
    self.assertEquals(id_list, [5])
    self.assertEquals(int(id_tool.dict_length_ids['foo'].value), 6)
    # Now, reinstall erp5_core, and make sure we still have the possibility
    # to continue generating ids
    cp_data = template_tool.manage_copyObjects(ids=(erp5_core_bt.getId(),))
    new_id = template_tool.manage_pasteObjects(cp_data)[0]['new_id']
    new_bt = template_tool[new_id]
    self.tic()
    self.commit()
    new_bt.install(force=1)
    erp5_core_bt.setRevision(1562)
    cp_data = custom_skin_folder.manage_cutObjects(ids=script_id_list)
    skin_folder.manage_pasteObjects(cp_data)
    id_list = id_tool.generateNewLengthIdList(id_group='foo')
    # it is known that with current upgrade there is a whole
    self.assertEquals(id_list, [7])
    new_id = id_tool.generateNewId(id_group='foo')
    self.assertEquals(new_id, 4)
    new_id = id_tool.generateNewId(id_group=('bar','baz'))
    self.assertEquals(new_id, 3)
    # Make sure that the old code is not used any more, so the dic on
    # id tool should not change, checking for length_dict
    self.assertEquals(int(id_tool.dict_length_ids['foo'].value), 6)
    id_list = id_tool.generateNewLengthIdList(id_group='bar')
    self.assertEquals(id_list, [11])
    generator_list = [x for x in id_tool.objectValues()
                      if x.getReference()=='mysql_non_continuous_increasing']
    self.assertEquals(len(generator_list), 1)
    generator = generator_list[0]
    self.assertEquals(generator.last_max_id_dict['foo'].value, 7)
    self.assertEquals(generator.last_max_id_dict['bar'].value, 11)
    # Make sure that the old code is not used any more, so the dic on
    # id tool should not change, checking for dict
    self.assertEquals(id_tool.dict_ids['foo'], 3)
    generator_list = [x for x in id_tool.objectValues()
                      if x.getReference()=='zodb_continuous_increasing']
    self.assertEquals(len(generator_list), 1)
    generator = generator_list[0]
    self.assertEquals(generator.last_id_dict['foo'], 4)
    self.assertEquals(generator.last_id_dict["('bar', 'baz')"], 3)
