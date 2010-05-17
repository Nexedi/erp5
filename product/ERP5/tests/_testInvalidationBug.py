# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors. 
# All Rights Reserved.
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
import os

import transaction

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import createZODBPythonScript
from DateTime import DateTime

class TestInvalidationBug(ERP5TypeTestCase):

  def getTitle(self):
    return "Invalidation Bug"

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base',)

  def afterSetUp(self):
    self.login()

  def testReindex(self):
    self.login()
    module = self.getPortalObject().organisation_module
    module.setIdGenerator('_generatePerDayId')
    module.migrateToHBTree()
    transaction.commit()
    self.tic()
    previous = DateTime()
    skin_folder = self.getPortal().portal_skins.custom
    if 'create_script' in skin_folder.objectIds():
      skin_folder.manage_delObjects(ids=['create_script'])
    skin = createZODBPythonScript(skin_folder, 'create_script', '**kw',
        """
from Products.ERP5Type.Log import log
id_list = []
for x in xrange(0, 1):
  organisation = context.newContent()
  id_list.append(organisation.getId())
log('Created Organisations', (context,id_list))
#log('All organisations', (context,[x for x in context.objectIds()]))
context.activate(activity='SQLQueue').create_script()
log('Organisation #', len(context))
""")
    for x in xrange(0,200):
      module.activate(activity='SQLQueue').create_script()
    transaction.commit()
    self.tic()

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestInvalidationBug))
  return suite
