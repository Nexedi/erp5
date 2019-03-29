# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#               Hervé Poulain <herve@nexedi.com>
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
from Products.ERP5TioSafe.tests.testPrestashopMixin import testPrestashopMixin

class TestPersonERP5Synchronization(testPrestashopMixin):
  """ This class allows to check different cases of Person's sync. """
  def afterSetUp(self):
    """ This method is called after the SetUp method. """
    # Shortcut for modules and tools
    self.person_module = self.portal.person_module
    self.connection = self.portal.erp5_sql_connection
    self.prestashop = self.portal.portal_integrations.prestashop
    self.root_xml = '<directory>\n%s\n</directory>'
    self.not_removable_id_list = [self.prestashop.getSourceAdministrationValue().getId(),
                                  self.prestashop.getResourceValue().getId(),
                                  self.prestashop.getDestinationValue().getId()]
    for stc in self.getPortalObject().sale_trade_condition_module.objectValues():
      if stc.getValidationState() == "draft":
        stc.validate()

  def test_PrestashopSimplestXMLSync(self):
    """ This test checks the person sync with the simplest XML. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_01.sql' %  self.ps_dump_path,
    )
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 2)
    person = self.person_module.contentValues()[0]
    self.assertEqual(person.getTitle(), 'John DOE')
    self.assertEqual(person.getFirstName(), 'John')
    self.assertEqual(person.getLastName(), 'DOE')
    self.assertEqual(person.getDefaultEmailText(), 'john@doe.com')
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % person.Node_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        xsd_path='../XSD/nodes.xsd',
    )

  def test_PrestashopPersonWithSingleAddressSync(self):
    """ This test checks the person sync with an address. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_02.sql' %  self.ps_dump_path,
    )
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 2)
    person = self.person_module.contentValues()[0]
    self.assertEqual(person.getTitle(), 'Jean GRAY')
    self.assertEqual(person.getFirstName(), 'Jean')
    self.assertEqual(person.getLastName(), 'GRAY')
    self.assertEqual(person.getDefaultEmailText(), 'jean@gray.com')
    self.assertEqual(str(person.getStartDate()), str(DateTime('1985-04-05')))
    self.assertEqual(len(person.searchFolder(portal_type='Address')), 1)
    self.assertEqual(
        person.getDefaultAddressStreetAddress(),
        '22 rue des Peupliers',
    )
    self.assertEqual(person.getDefaultAddressZipCode(), '75000')
    self.assertEqual(person.getDefaultAddressCity(), 'Paris')
    self.assertEqual(person.getDefaultAddressRegionTitle(), 'France')
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % person.Node_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        xsd_path='../XSD/nodes.xsd',
    )

  def test_PrestashopPersonWithMultipleAddressSync(self):
    """ This test checks the person sync with the simplest XML. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_03.sql' %  self.ps_dump_path,
    )
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 2)
    person = self.person_module.contentValues()[0]
    self.assertEqual(person.getTitle(), 'Jenifer-Dylan COX')
    self.assertEqual(person.getFirstName(), 'Jenifer-Dylan')
    self.assertEqual(person.getLastName(), 'COX')
    self.assertEqual(person.getDefaultEmailText(), 'jenifer-dylan@cox.com')
    self.assertEqual(str(person.getStartDate()), str(DateTime('2008-06-06')))
    self.assertEqual(len(person.searchFolder(portal_type='Address')), 3)
    for address in person.searchFolder(portal_type='Address'):
      index = address.getId()
      if index == 'default_address':
        self.assertEqual(
            address.getStreetAddress(),
            '123 boulevard des Capucines',
        )
        self.assertEqual(address.getZipCode(), '72160')
        self.assertEqual(address.getCity(), 'Stuttgart')
        self.assertEqual(address.getRegionTitle(), 'Allemagne')
      elif index == '2':
        self.assertEqual(
            address.getStreetAddress(),
            '234 rue de la Paix',
        )
        self.assertEqual(address.getZipCode(), '75000')
        self.assertEqual(address.getCity(), 'Paris')
        self.assertEqual(address.getRegionTitle(), 'France')
      elif index == '3':
        self.assertEqual(address.getStreetAddress(), '345 avenue des Fleurs')
        self.assertEqual(address.getZipCode(), '44001')
        self.assertEqual(address.getCity(), 'Dortmund')
        self.assertEqual(address.getRegionTitle(), 'Allemagne')
      else:
        raise ValueError('Can not check the address: %s of the person: %s' % \
            (address.getId(), person.getTitle()))
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % person.Node_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        xsd_path='../XSD/nodes.xsd',
    )

  def test_PrestashopPersonWithAddressNoMappingSync(self):
    """ This test checks the person sync with an address and no mapping. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_04.sql' %  self.ps_dump_path,
    )
    self.tic()

    # Check that an empty mapping is created in integration site
    self.assertTrue(self.prestashop.get('Country', None) is None)
    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 1)

  def test_PrestashopDeletePerson(self):
    """ Check that the delete during a person's sync invalidate the person. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_05.sql' %  self.ps_dump_path,
    )
    self.tic()

    # Run the sync of persons
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 4)
    # Move the persons as draft, validated and invalidated state
    john_doe = self.person_module.searchFolder(
        portal_type='Person',
        title='John DOE',
    )[0].getObject()
    jane_doe = self.person_module.searchFolder(
        portal_type='Person',
        title='Jane DOE',
    )[0].getObject()
    if jane_doe.getValidationState() != "validated":
      jane_doe.validate()
    dan_doe = self.person_module.searchFolder(
        portal_type='Person',
        title='Dan DOE',
    )[0].getObject()
    if dan_doe.getValidationState() != "validated":
      dan_doe.validate()
    dan_doe.invalidate()
    # Remove the persons in prestashop and check that after sync the state
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_06.sql' %  self.ps_dump_path,
    )
    self.tic()
    self.assertEqual(john_doe.getValidationState(), 'validated')
    self.assertEqual(jane_doe.getValidationState(), 'validated')
    self.assertEqual(dan_doe.getValidationState(), 'invalidated')
    for stc in self.getPortalObject().sale_trade_condition_module.objectValues():
      self.assertEqual(stc.getValidationState(), "validated")
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 4)
    # State of person does not change, this removal is managed through trade condition
    self.assertEqual(john_doe.getValidationState(), 'validated')
    self.assertEqual(jane_doe.getValidationState(), 'validated')
    self.assertEqual(dan_doe.getValidationState(), 'invalidated')
    deleted_person_list = (john_doe.getRelativeUrl(),
                           jane_doe.getRelativeUrl(),
                           dan_doe.getRelativeUrl())
    for stc in self.getPortalObject().sale_trade_condition_module.objectValues():
      if stc.getDestination() in deleted_person_list:
        self.assertEqual(stc.getValidationState(), "invalidated")
      else:
        self.assertEqual(stc.getValidationState(), "validated")

  def test_PrestashopUpdateSimpleElement(self):
    """ This test checks the simple update after sync of persons. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_07.sql' %  self.ps_dump_path,
    )
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 2)
    person = self.person_module.contentValues()[0]
    self.assertEqual(person.getTitle(), 'Chris TURK')
    self.assertEqual(person.getFirstName(), 'Chris')
    self.assertEqual(person.getLastName(), 'TURK')
    self.assertEqual(person.getDefaultEmailText(), 'chris@turk.com')
    self.assertEqual(str(person.getStartDate()), str(DateTime('1980-06-22')))
    self.assertEqual(len(person.searchFolder(portal_type='Address')), 1)
    self.assertEqual(
        person.getDefaultAddressStreetAddress(),
        '22 rue des Peupliers',
    )
    self.assertEqual(person.getDefaultAddressZipCode(), '75000')
    self.assertEqual(person.getDefaultAddressCity(), 'Paris')
    self.assertEqual(person.getDefaultAddressRegionTitle(), 'France')
    # Update the data, run the sync and check the data after the update
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_08.sql' % self.ps_dump_path,
    )
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 2)
    self.assertEqual(person.getTitle(), 'Chris TURK')
    self.assertEqual(person.getFirstName(), 'Chris')
    self.assertEqual(person.getLastName(), 'TURK')
    self.assertEqual(person.getDefaultEmailText(), 'chris@turk.com')
    self.assertEqual(str(person.getStartDate()), str(DateTime('1974-06-22')))
    self.assertEqual(len(person.searchFolder(portal_type='Address')), 1)
    self.assertEqual(
        person.getDefaultAddressStreetAddress(),
        '22 rue des Peupliers',
    )
    self.assertEqual(person.getDefaultAddressZipCode(), '75000')
    self.assertEqual(person.getDefaultAddressCity(), 'Paris')
    self.assertEqual(person.getDefaultAddressRegionTitle(), 'France')
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % person.Node_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        xsd_path='../XSD/nodes.xsd',
    )

  def test_PrestashopComplexeUpdateElement(self):
    """
      This test checks the complexe update after sync of persons.
      It updates some element, adds others and removes the last.
    """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_09.sql' %  self.ps_dump_path,
    )
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.person_module.contentValues()), 1)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 2)
    person = self.person_module.contentValues()[0]
    self.assertEqual(person.getTitle(), 'Perry COX')
    self.assertEqual(person.getFirstName(), 'Perry')
    self.assertEqual(person.getLastName(), 'COX')
    self.assertEqual(person.getDefaultEmailText(), 'perry@cox.com')
    self.assertEqual(str(person.getStartDate()), str(DateTime('1959-08-03')))
    address_list = person.searchFolder(
        portal_type='Address',
        sort_on=(['id', 'ASC'], ),
    )
    self.assertEqual(len(address_list), 2)
    for index, address in enumerate(address_list):
      if index == 0:
        self.assertEqual(address.getStreetAddress(), '789 avenue des Fleurs')
        self.assertEqual(address.getZipCode(), '44001')
        self.assertEqual(address.getCity(), 'Dortmund')
        self.assertEqual(address.getRegionTitle(), 'Allemagne')
      elif index == 1:
        self.assertEqual(address.getStreetAddress(), '456 rue de la Paix')
        self.assertEqual(address.getZipCode(), '75000')
        self.assertEqual(address.getCity(), 'Paris')
        self.assertEqual(address.getRegionTitle(), 'France')
      else:
        raise ValueError('Can not check the address: %s of the person: %s' % \
            (index, person.getTitle()))
    # The first update check remove of simple element, remove an address
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_10.sql' % self.ps_dump_path,
    )
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(person.getTitle(), 'Perry COX')
    self.assertEqual(person.getFirstName(), 'Perry')
    self.assertEqual(person.getLastName(), 'COX')
    self.assertEqual(person.getDefaultEmailText(), 'perry@cox.com')
    self.assertEqual(person.getStartDate(), None)
    self.assertEqual(len(person.searchFolder(portal_type='Address')), 1)
    self.assertEqual(
        person.getDefaultAddressStreetAddress(),
        '123 boulevard des Capucines',
    )
    self.assertEqual(person.getDefaultAddressZipCode(), '72160')
    self.assertEqual(person.getDefaultAddressCity(), 'Stuttgart')
    self.assertEqual(person.getDefaultAddressRegionTitle(), 'Allemagne')
    # The second update check the add of a simple element and the add of
    # address
    self.loadSQLDump(
        self.connection,
        '%s/dump_person_sync_11.sql' % self.ps_dump_path,
    )
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(person.getTitle(), 'Perry COX')
    self.assertEqual(person.getFirstName(), 'Perry')
    self.assertEqual(person.getLastName(), 'COX')
    self.assertEqual(person.getDefaultEmailText(), 'perry@cox.com')
    self.assertEqual(str(person.getStartDate()), str(DateTime('1959-08-03')))
    address_list = person.searchFolder(
        portal_type='Address',
        sort_on=(['id', 'ASC'], ),
    )
    self.assertEqual(len(address_list), 2)
    for index, address in enumerate(address_list):
      if index == 0:
        self.assertEqual(address.getStreetAddress(), '789 avenue des Fleurs')
        self.assertEqual(address.getZipCode(), '44001')
        self.assertEqual(address.getCity(), 'Dortmund')
        self.assertEqual(address.getRegionTitle(), 'Allemagne')
      elif index == 1:
        self.assertEqual(
            address.getStreetAddress(),
            '123 boulevard des Capucines',
        )
        self.assertEqual(address.getZipCode(), '72160')
        self.assertEqual(address.getCity(), 'Stuttgart')
        self.assertEqual(address.getRegionTitle(), 'Allemagne')
      else:
        raise ValueError('Can not check the address: %s of the person: %s' % \
            (index, person.getTitle()))
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % person.Node_asTioSafeXML(),
        tiosafe_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        xsd_path='../XSD/nodes.xsd',
    )

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPersonERP5Synchronization))
  return suite
