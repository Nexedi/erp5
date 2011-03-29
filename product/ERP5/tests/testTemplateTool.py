# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurelien Calonne <aurel@nexedi.com>
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

class TestTemplateTool(ERP5TypeTestCase):
  """
  Test the template tool
  """
  run_all_test = 1
  quiet = 1

  def getBusinessTemplateList(self):
    return ('erp5_base', )

  def getTitle(self):
    return "Template Tool"

  def afterSetUp(self):
    self.templates_tool = self.portal.portal_templates

  def testUpdateBT5FromRepository(self, quiet=quiet, run=run_all_test):
    """ Test the list of bt5 returned for upgrade """
    # edit bt5 revision so that it will be marked as updatable
    bt_list = self.templates_tool.searchFolder(title='erp5_base')
    self.assertEquals(len(bt_list), 1)
    erp5_base = bt_list[0].getObject()
    erp5_base.edit(revision=int(erp5_base.getRevision()) - 10)
    self.templates_tool.updateRepositoryBusinessTemplateList(\
                 ["http://www.erp5.org/dists/snapshot/bt5/",])

    updatable_bt_list = self.templates_tool.getRepositoryBusinessTemplateList(update_only=True)
    self.assertEqual(
           [i.title for i in updatable_bt_list if i.title == "erp5_base"], 
           ["erp5_base"])
    erp5_base.replace()
    updatable_bt_list = self.templates_tool.getRepositoryBusinessTemplateList(update_only=True)
    self.assertEqual(
           [i.title for i in updatable_bt_list if i.title == "erp5_base"],
           [])


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTemplateTool))
  return suite
