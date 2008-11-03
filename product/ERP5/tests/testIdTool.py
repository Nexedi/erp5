##############################################################################
# -*- coding: utf8 -*-
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurélien Calonne <aurel@nexedi.com>
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
from DateTime import DateTime
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ZSQLCatalog.SQLCatalog import Query

class TestIdTool(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  resource_type='Apparel Component'
  resource_variation_type='Apparel Component Variation'
  resource_module = 'apparel_component_module'

  def getTitle(self):
    """
    """
    return "Id Tool"

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

    """
    return ()

  def test_getLastLengthGeneratedId(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Check getLastLengthGeneratedId method')
    idtool = self.portal.portal_ids
    # test with value stored into zodb
    new_id = idtool.generateNewLengthId(id_group=4, store=1)
    get_transaction().commit()
    self.tic()
    last_id = idtool.getLastLengthGeneratedId(id_group=4)
    self.assertEqual(new_id, last_id)
    # same test without storing value into zodb
    new_id = idtool.generateNewLengthId(id_group=5, store=0)
    get_transaction().commit()
    self.tic()
    last_id = idtool.getLastLengthGeneratedId(id_group=5)
    self.assertEqual(new_id, last_id)
    # test with id_group as tuple
    new_id = idtool.generateNewLengthId(id_group=(6,), store=0)
    get_transaction().commit()
    self.tic()
    last_id = idtool.getLastLengthGeneratedId(id_group=(6,),)
    self.assertEqual(new_id, last_id)
    # test default value
    last_id = idtool.getLastLengthGeneratedId(id_group=(7,),)
    self.assertEqual(None, last_id)
    last_id = idtool.getLastLengthGeneratedId(id_group=8,default=99)
    self.assertEqual(99, last_id)
    

  def test_generateNewId(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Check generateNewId method')
    idtool = self.portal.portal_ids
    # id tool generate ids based on a group
    self.assertEquals(0, idtool.generateNewId(id_group=('a', 'b')))
    self.assertEquals(1, idtool.generateNewId(id_group=('a', 'b')))
    # different groups generate different ids
    self.assertEquals(0, idtool.generateNewId(id_group=('a', 'b', 'c')))

    self.assertEquals(2, idtool.generateNewId(id_group=('a', 'b')))
    self.assertEquals(1, idtool.generateNewId(id_group=('a', 'b', 'c')))
      
    # you can pass an initial value
    self.assertEquals(4, idtool.generateNewId(id_group=('a', 'b', 'c', 'd'),
                                                default=4))
    self.assertEquals(5, idtool.generateNewId(id_group=('a', 'b', 'c', 'd'),
                                                default=4))
    #method to generate a special number                                            
    def generateTestNumber(last_id):
       return ('A%s'%(last_id))
      # you can pass a method
    self.assertEquals('A0', idtool.generateNewId(id_group=('c', 'd'),
                                                method=generateTestNumber))
    self.assertEquals('AA0', idtool.generateNewId(id_group=('c', 'd'),
                                                method=generateTestNumber))
    
    self.assertEquals('AA', idtool.generateNewId(id_group=('c', 'd', 'e'),
                                                default='A',
                                                method=generateTestNumber))
    self.assertEquals('AAA', idtool.generateNewId(id_group=('c', 'd', 'e'),
                                                default='A',
                                                method=generateTestNumber))

  def test_generateNewLongId(self):
    idtool = self.portal.portal_ids
    # test with value stored into zodb
    new_id = idtool.generateNewLongId()
    self.assertTrue(isinstance(new_id, long))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestIdTool))
  return suite

