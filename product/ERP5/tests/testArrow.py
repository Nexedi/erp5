##############################################################################
#
# Copyright (c) 2013 Nexedi KK and Contributors. All Rights Reserved.
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

class TestArrow(ERP5TypeTestCase):

  def getTitle(self):
    return "Arrow property Sheet Test"

  def getBusinessTemplateList(self):
    """ return business template list """
    return ('erp5_base',)

  def test_01_testGetterSetter(self):
    """
     Test the getter/setter of Arrow properties.
    """
    person_module = self.portal.person_module
    person = person_module.newContent(portal_type='Person')
    career = person.newContent(portal_type='Career')
    person_sda = person_module.newContent(portal_type='Person', id='sda')
    person_dda = person_module.newContent(portal_type='Person', id='dda')
    person_sca = person_module.newContent(portal_type='Person', id='sca')
    person_dca = person_module.newContent(portal_type='Person', id='dca')
    person_ssa = person_module.newContent(portal_type='Person', id='ssa')
    person_dsa = person_module.newContent(portal_type='Person', id='dsa')

    # Career portal type provides Arrow properties
    # so here we use Career testing Arrow
    career.setSourceDecisionAdministrationValue(person_sda)
    career.setDestinationDecisionAdministrationValue(person_dda)
    career.setSourceCarrierAdministrationValue(person_sca)
    career.setDestinationCarrierAdministrationValue(person_dca)
    career.setSourceSectionAdministrationValue(person_ssa)
    career.setDestinationSectionAdministrationValue(person_dsa)

    self.assertEqual(career.getSourceDecisionAdministrationValue(), person_sda)
    self.assertEqual(career.getDestinationDecisionAdministrationValue(),
                     person_dda)
    self.assertEqual(career.getSourceCarrierAdministrationValue(), person_sca)
    self.assertEqual(career.getDestinationCarrierAdministrationValue(),
                     person_dca)
    self.assertEqual(career.getSourceSectionAdministrationValue(), person_ssa)
    self.assertEqual(career.getDestinationSectionAdministrationValue(),
                     person_dsa)

    # set the parent document to the property
    # make sure it is not confusing because of acquisition
    career.setSourceDecisionAdministrationValue(person)
    self.assertEqual(career.getSourceDecisionAdministrationValue(), person)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestArrow))
  return suite
