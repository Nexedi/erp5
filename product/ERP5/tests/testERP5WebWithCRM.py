# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Nicolas Delaby <nicolas@nexedi.com>
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
import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase,\
     _getConversionServerDict


class TestERP5WebWithCRM(ERP5TypeTestCase):
  """Test for erp5_web and erp5_crm features
  """

  def getTitle(self):
    return "ERP5 Web with CRM"

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_base',
            'erp5_ingestion',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_crm',
            'erp5_jquery',
            'erp5_web',
            )

  def afterSetUp(self):
    self.login()
    self.setSystemPreference()
    user = self.createUser('robby')
    self.createUserAssignment(user, {})

  def setSystemPreference(self):
    portal_type = 'System Preference'
    preference_list = self.portal.portal_preferences.contentValues(
                                                       portal_type=portal_type)
    if not preference_list:
      preference = self.portal.portal_preferences.newContent(
                                                       portal_type=portal_type)
    else:
      preference = preference_list[0]
    conversion_dict = _getConversionServerDict()
    preference.setPreferredOoodocServerAddress(conversion_dict['hostname'])
    preference.setPreferredOoodocServerPortNumber(conversion_dict['port'])
    if self.portal.portal_workflow.isTransitionPossible(preference, 'enable'):
      preference.enable()

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    transaction.commit()
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.web_site_module)
    self.clearModule(self.portal.event_module)
    self.clearModule(self.portal.person_module)

  def setupWebSection(self, **kw):
    """
      Setup Web Site
    """
    portal = self.getPortal()
    website = self.getPortal().web_site_module.newContent(portal_type='Web Site',
                                                          **kw)
    websection = website.newContent(portal_type='Web Section', **kw)
    website.publish()
    transaction.commit()
    self.tic()
    return websection

  def test_01_Contact_Us_with_Anonymous_user(self):
    """Test creation of Web Message with Anonymous User
    """
    web_section = self.setupWebSection()
    self.logout()
    form_kw = {'source_organisation_title': 'John Doe Industries',
               'source_person_first_name': 'John',
               'source_person_last_name': 'Doe',
               'source_person_default_email_text': 'John.Doe@example.com',
               'source_person_default_telephone_text': '34343434',
               'text_content': 'I want ERP5 for my company',
              }
    web_section.WebSection_addWebMessage(**form_kw)
    transaction.commit()
    self.tic()

    self.login()
    # Now a web message has been created
    event = self.portal.event_module.objectValues()[0]
    for property_id, value in form_kw.iteritems():
      self.assertEquals(event.getProperty(property_id), value)
    self.assertEquals(event.getSourceCarrier(), web_section.getRelativeUrl())
    self.assertTrue(event.hasStartDate())

    # Trig alarm execution
    self.portal.portal_alarms.fetch_incoming_web_message_list.activeSense()
    transaction.commit()
    self.tic()
    self.assertEquals(event.getSimulationState(), 'new')

  def test_02_Contact_Us_with_Aunthenticated_user(self):
    """Test creation of Web Message with Authenticted User
    """
    web_section = self.setupWebSection()
    self.logout()
    self.login('robby')
    form_kw = {'source_organisation_title': 'John Doe Industries',
               'source_person_first_name': 'John',
               'source_person_last_name': 'Doe',
               'source_person_default_email_text': 'John.Doe@example.com',
               'source_person_default_telephone_text': '34343434',
               'text_content': 'I want ERP5 for my company',
              }
    web_section.WebSection_addWebMessage(**form_kw)
    transaction.commit()
    self.tic()
    self.logout()

    self.login()
    # Now a web message has been created
    event = self.portal.event_module.objectValues()[0]
    for property_id, value in form_kw.iteritems():
      self.assertEquals(event.getProperty(property_id), value)
    self.assertEquals(event.getSourceCarrier(), web_section.getRelativeUrl())
    self.assertTrue(event.hasStartDate())
    self.assertTrue(event.hasSource()) # User was connected
                                       # he became source of event

    # Trig alarm execution
    self.portal.portal_alarms.fetch_incoming_web_message_list.activeSense()
    transaction.commit()
    self.tic()
    self.assertEquals(event.getSimulationState(), 'new')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5WebWithCRM))
  return suite
