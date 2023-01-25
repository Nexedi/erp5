##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestERP5SocialContracts(ERP5TypeTestCase):
  """Test for erp5_social_contracts business template.
  """
  def afterSetUp(self):
    self.person_1 = self.portal.person_module.newContent(
                                      portal_type='Person',
                                      birthday='2001-01-01',
                                      title='Person1')
    self.person_2 = self.portal.person_module.newContent(
                                      portal_type='Person',
                                      birthday='2002-02-02',
                                      title='Person2')
    self.person_3 = self.portal.person_module.newContent(
                                      portal_type='Person',
                                      birthday='2003-03-03',
                                      title='Person3')

  def beforeTearDown(self):
    self.abort()
    self.portal.person_module.manage_delObjects(
            list(self.portal.person_module.objectIds()))
    self.portal.social_contract_module.manage_delObjects(
            list(self.portal.social_contract_module.objectIds()))
    self.tic()

  def test_getChildCount(self):
    self.assertEqual(0, self.person_1.Person_getChildCount())

    self.person_2.setNaturalParentValue(self.person_1)
    self.tic()
    self.assertEqual(1, self.person_1.Person_getChildCount())

    self.assertEqual(1, self.person_1.Person_getChildCount(max_age=1000))
    self.assertEqual(0, self.person_1.Person_getChildCount(max_age=2))


  def test_SocialContract(self):
    self.assertEqual(0, self.person_1.Person_getPartnerCount())
    contract_1 = self.portal.social_contract_module.newContent(
                          portal_type='Social Contract',
                          social_contract_type='marriage',
                          start_date='2001-01-01')
    contract_1.setDestinationValueList((self.person_1, self.person_2))
    contract_1.validate()
    self.tic()
    self.assertEqual(1, self.person_1.Person_getPartnerCount())

    contract_2 = self.portal.social_contract_module.newContent(
                          portal_type='Social Contract',
                          start_date='2002-02-02')
    contract_2.setDestinationValueList((self.person_1, self.person_3))
    contract_2.setStopDate('3000-01-01')
    contract_2.validate()

    self.tic()
    self.assertEqual(2, self.person_1.Person_getPartnerCount())

    # you can specify a date
    self.assertEqual(1,
      self.person_1.Person_getPartnerCount(at_date=DateTime(3000, 1, 2)))

    # you can restrict to some social contracts types only
    self.assertEqual(1, self.person_1.Person_getPartnerCount(
                      valid_social_contract_type_list=('marriage', )))

    # only validated social contracts are used
    contract_1.invalidate()
    self.assertEqual(1, self.person_1.Person_getPartnerCount())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5SocialContracts))
  return suite

