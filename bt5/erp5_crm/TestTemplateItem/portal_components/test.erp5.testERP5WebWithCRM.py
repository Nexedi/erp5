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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import six


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
    user = self.createUser('robby')
    self.createUserAssignment(user, {})

  def clearModule(self, module):
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def beforeTearDown(self):
    self.clearModule(self.portal.web_site_module)
    self.clearModule(self.portal.event_module)
    self.clearModule(self.portal.person_module)

  def setupWebSection(self, **kw):
    """
      Setup Web Site
    """
    website = self.getPortal().web_site_module.newContent(portal_type='Web Site',
                                                          **kw)
    websection = website.newContent(portal_type='Web Section', **kw)
    website.publish()
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
    self.tic()

    self.login()
    # Now a web message has been created
    telephone_key = 'source_person_default_telephone_text'
    event = self.portal.event_module.objectValues()[0]
    for property_id, value in six.iteritems(form_kw):
      if property_id == telephone_key:
        value =  '+(0)-%s' % value

      self.assertEqual(event.getProperty(property_id), value)
    self.assertEqual(event.getSourceCarrier(), web_section.getRelativeUrl())
    self.assertTrue(event.hasStartDate())

    # Trig alarm execution
    self.portal.portal_alarms.fetch_incoming_web_message_list.activeSense()
    self.tic()
    self.assertEqual(event.getSimulationState(), 'delivered')
    ticket = event.getFollowUpValue()
    self.assertTrue(ticket is not None)
    self.assertEqual(ticket.getSimulationState(), 'submitted')
    person = event.getSourceValue()
    self.assertTrue(person is not None)
    self.assertEqual(person.getFirstName(),
                      form_kw['source_person_first_name'])
    self.assertEqual(person.getLastName(),
                      form_kw['source_person_last_name'])
    self.assertEqual(person.getDefaultEmailText(),
                      form_kw['source_person_default_email_text'])
    self.assertIn(form_kw['source_person_default_telephone_text'],\
                    person.getDefaultTelephoneText())
    self.assertEqual(person.getValidationState(), 'validated')
    organisation = person.getSubordinationValue()
    self.assertTrue(organisation is not None)
    self.assertEqual(organisation.getValidationState(), 'validated')
    self.assertEqual(organisation.getTitle(),
                      form_kw['source_organisation_title'])

  def test_02_Contact_Us_with_Aunthenticated_user(self):
    """Test creation of Web Message with Authenticated User
    """
    web_section = self.setupWebSection()
    self.logout()
    self.loginByUserName('robby')
    form_kw = {'source_organisation_title': 'John Doe Industries',
               'source_person_first_name': 'John',
               'source_person_last_name': 'Doe',
               'source_person_default_email_text': 'John.Doe@example.com',
               'source_person_default_telephone_text': '34343434',
               'text_content': 'I want ERP5 for my company',
              }
    web_section.WebSection_addWebMessage(**form_kw)
    transaction.commit()
    # here we check a random bug caused by the ordering of activities
    event_module_path_prefix = self.portal.event_module.getPath() + '/'
    deprioritize_message_list = []
    # we'll stop whenever we find the message that reindex the newly created
    # event object
    def stop_condition(message_list):
      for message in message_list:
        object_path = '/'.join(message.object_path)
        if (message.method_id == 'immediateReindexObject' and
            object_path.startswith(event_module_path_prefix)):
          deprioritize_message_list.append(message)
          return True
      return False
    self.tic(stop_condition=stop_condition)
    assert len(deprioritize_message_list) == 1
    web_message_reindex_message = deprioritize_message_list[0]
    web_message_path = web_message_reindex_message.object_path
    self.assertTrue(
      self.portal.unrestrictedTraverse(web_message_path).getPortalType(),
      'Web Message',
    )
    # we'll deprioritize this message, so it executes last of all
    self.portal.cmf_activity_sql_connection.manage_test("""
      update message set priority=100
      where uid=%s
    """ % web_message_reindex_message.uid)
    transaction.commit()
    self.tic()
    self.logout()

    self.login()
    telephone_key = "source_person_default_telephone_text"
    # Now a web message has been created
    event = self.portal.event_module.objectValues()[0]
    for property_id, value in six.iteritems(form_kw):
      if property_id == telephone_key:
        value =  '+(0)-%s' % value
      self.assertEqual(event.getProperty(property_id), value)

    self.assertEqual(event.getSourceCarrier(), web_section.getRelativeUrl())
    self.assertTrue(event.hasStartDate())
    self.assertTrue(event.hasSource()) # User was connected
                                       # he became source of event

    # Trig alarm execution
    self.portal.portal_alarms.fetch_incoming_web_message_list.activeSense()
    self.tic()
    self.assertEqual(event.getSimulationState(), 'delivered')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5WebWithCRM))
  return suite
