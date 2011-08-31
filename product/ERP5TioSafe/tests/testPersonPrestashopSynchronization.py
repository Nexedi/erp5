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

import transaction
from Products.ERP5TioSafe.tests.testPrestashopMixin import testPrestashopMixin

class TestPersonPrestashopSynchronization(testPrestashopMixin):
  """ This class allows to check different cases of Person's sync. """
  def afterSetUp(self):
    """ This method is called after the SetUp method. """
    # Shortcut for modules and tools
    self.person_module = self.portal.person_module
    self.portal_sync= self.portal.portal_synchronizations
    self.prestashop = self.portal.portal_integrations.prestashop
    self.root_xml = '<directory>\n%s\n</directory>'

  def createPerson(self, **kw):
    """
     This method create the person and the related sale trade condition
    """
    person = self.person_module.newContent(**kw)
    person.validate()
    person_url = person.getRelativeUrl()
    stc = self.getPortalObject().sale_trade_condition_module.newContent(destination=person_url,
                                                                        destination_secion=person_url,
                                                                        destination_decision=person_url,
                                                                        destination_administration=person_url,
                                                                        specialise=self.prestashop.getSourceTrade())
    stc.validate()
    transaction.commit()
    self.tic()
    return person

  def test_PrestashopSimplestXMLSync(self):
    """ This test checks the person sync with the simplest XML. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    person = self.createPerson(
        portal_type='Person',
        title='John DOE',
        first_name='John',
        last_name='DOE',
        default_email_text='john@doe.com',
        career_role_list = ['client'],
    )
    
    transaction.commit()
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.prestashop.person_module()), 0)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        tiosafe_xml=self.root_xml % person.Node_asTioSafeXML(),
        xsd_path='../XSD/nodes.xsd',
    )

  def test_PrestashopPersonWithSingleAddressSync(self):
    """ This test checks the person sync with an address. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    person = self.createPerson(
        portal_type='Person',
        title='Jean GRAY',
        first_name='Jean',
        last_name='GRAY',
        start_date='1985-04-05',
        default_email_text='jean@gray.com',
        career_role_list = ['client'],
    )
    person.setDefaultAddressStreetAddress('22 rue des Peupliers')
    person.setDefaultAddressZipCode('75000')
    person.setDefaultAddressCity('Paris')
    person.setDefaultAddressRegion('france')
    
    transaction.commit()
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.prestashop.person_module()), 0)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        tiosafe_xml=self.root_xml % person.Node_asTioSafeXML(),
        xsd_path='../XSD/nodes.xsd',
    )

  def test_PrestashopPersonWithMultipleAddressSync(self):
    """ This test checks the person sync with the simplest XML. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    person = self.createPerson(
        portal_type='Person',
        title='Jenifer-Dylan COX',
        first_name='Jenifer-Dylan',
        last_name='COX',
        start_date='2008-06-06',
        default_email_text='jenifer-dylan@cox.com',
        career_role_list = ['client'],
    )
    # default address
    person.setDefaultAddressStreetAddress('123 boulevard des Capucines')
    person.setDefaultAddressZipCode('72160')
    person.setDefaultAddressCity('Stuttgart')
    person.setDefaultAddressRegion('europe/western_europe/allemagne')
    person.default_address.setIntIndex(1)
    # second address
    person.newContent(
        portal_type='Address',
        id='2',
        street_address='234 rue de la Paix',
        zip_code='75000',
        city='Paris',
        region='france',
        int_index=2,
    )
    # third address
    person.newContent(
        portal_type='Address',
        id='3',
        street_address='345 avenue des Fleurs',
        zip_code='44001',
        city='Dortmund',
        region='europe/western_europe/allemagne',
        int_index=3,
    )
    transaction.commit()
    self.tic()
    
    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.prestashop.person_module()), 0)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        tiosafe_xml=self.root_xml % person.Node_asTioSafeXML(),
        xsd_path='../XSD/nodes.xsd',
    )

  def test_PrestashopDeletePerson(self):
    """ Check that the delete during a person's sync invalidate the person. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    person = self.createPerson(
        portal_type='Person',
        title='John DOE',
        first_name='John',
        last_name='DOE',
        default_email_text='john@doe.com',
        career_role_list = ['client'],
    )
    
    transaction.commit()
    self.tic()

    # Run the sync of persons
    self.assertEqual(len(self.prestashop.person_module()), 0)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    # Remove the persons in ERP5 and check that after sync in prestashop
    self.person_module.manage_delObjects([person.getId(), ])
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.person_module.contentValues()), 0)

  def test_PrestashopUpdateSimpleElement(self):
    """ This test checks the simple update after sync of persons. """
    # Initialize the instance and prestashop
    self.initPrestashopTest()
    self.initMapping(self.prestashop)
    person = self.createPerson(
        portal_type='Person',
        title='Chris TURK',
        first_name='Chris',
        last_name='TURK',
        default_email_text='chris@turk.com',
        default_address_street_address='22 rue des Peupliers',
        default_address_zip_code='75000',
        default_address_city='Paris',
        default_address_region='france',
        career_role_list = ['client'],
    )
    
    transaction.commit()
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.prestashop.person_module()), 0)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        tiosafe_xml=self.root_xml % person.Node_asTioSafeXML(),
        xsd_path='../XSD/nodes.xsd',
    )
    # Update the data, run the sync and check the data after the update
    person.setStartDate('1974-06-22')
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    # Check the XML schema and the fixed point
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        tiosafe_xml=self.root_xml % person.Node_asTioSafeXML(),
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
    person = self.createPerson(
        portal_type='Person',
        title='Perry COX',
        first_name='Perry',
        last_name='COX',
        default_email_text='perry@cox.com',
        start_date='1959-08-03',
        default_address_street_address='456 rue de la Paix',
        default_address_zip_code='75000',
        default_address_city='Paris',
        default_address_region='france',
        career_role_list = ['client'],
    )
    person.default_address.setIntIndex(1)
    address2 = person.newContent(
        portal_type='Address',
        street_address='789 avenue des Fleurs',
        zip_code='44001',
        city='Dortmund',
        int_index=2,
        region='europe/western_europe/allemagne',
    )
    transaction.commit()
    self.tic()

    # Run the sync of persons and check person's data after sync
    self.assertEqual(len(self.prestashop.person_module()), 0)
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        tiosafe_xml=self.root_xml % person.Node_asTioSafeXML(),
        xsd_path='../XSD/nodes.xsd',
    )
    # The first update check remove of simple element, remove an address
    person.setStartDate(None)
    person.manage_delObjects([address2.getId(), ])
    person.setDefaultAddressStreetAddress('123 boulevard des Capucines')
    person.setDefaultAddressZipCode('72160')
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        tiosafe_xml=self.root_xml % person.Node_asTioSafeXML(),
        xsd_path='../XSD/nodes.xsd',
    )
    # The second update check the add of a simple element and the add of
    # address
    person.setStartDate('1959-08-03') # TODO: Why it doesn't work ???
    person.setDefaultAddressCity('Lille')
    address2 = person.newContent(
        portal_type='Address',
        street_address='789 avenue des Fleurs',
        zip_code='44001',
        city='Dortmund',
        region='europe/western_europe/allemagne',
        int_index=3,
    )
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        tiosafe_xml=self.root_xml % person.Node_asTioSafeXML(),
        xsd_path='../XSD/nodes.xsd',
    )
    # The third update check the remove of element in addresses
    person.setDefaultAddressZipCode('73000')
    address2.setCity('Munich')
    self.loadSync([self.prestashop.person_module, ])
    self.assertEqual(len(self.prestashop.person_module()), 1)
    self.checkTioSafeXML(
        plugin_xml=self.root_xml % self.prestashop.person_module()[0].asXML(),
        tiosafe_xml=self.root_xml % person.Node_asTioSafeXML(),
        xsd_path='../XSD/nodes.xsd',
    )

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestPersonPrestashopSynchronization))
  return suite
