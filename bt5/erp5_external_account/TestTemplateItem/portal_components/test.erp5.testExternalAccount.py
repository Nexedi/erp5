# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004, 2005, 2006 Nexedi SARL and Contributors.
# All Rights Reserved.
#          Ivan Tyagov <ivan@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

class TestExternalAccount(ERP5TypeTestCase):
  """
  Test for erp5_authentication_policy business template.
  """
  def getTitle(self):
    return "TestExternalAccount"

  def getBusinessTemplateList(self):
    """
    Return the list of required business templates.
    """
    return ('erp5_core_proxy_field_legacy',
            'erp5_base',
            'erp5_ingestion_mysql_innodb_catalog',
            'erp5_external_account',)

  def afterSetUp(self):
    portal = self.getPortal()

    # Setup auth policy
    preference = portal.portal_preferences.newContent(
                                             portal_type = 'System Preference',
                                             title = 'External Account',
                                             preferred_managed_external_domain_name_list = ['erp5.org'])
    preference.enable()
    self.tic()


  # Email Account in external_account_module is not "invalidated" as it is not
  # indexed in email table.
  @unittest.expectedFailure
  def test_01_PersonExternalEmailAccountCreation(self):
    """
      Test that external account creation.
    """
    portal = self.getPortal()
    person = portal.person_module.newContent(first_name = 'First',
                                             last_name = 'Last',
                                             default_email_text = 'ivan@erp5.org')
    person.validate()
    career = person.newContent(portal_type = 'Career',
                               title = 'Career 0')
    career.start()
    self.tic()
    self.assertEqual(1, len(portal.external_account_module.objectValues()))
    self.assertEqual(person, portal.external_account_module.objectValues()[0].getSourceValue())
    self.assertEqual(person.Person_getDefaultExternalEmailText(), \
                     portal.external_account_module.objectValues()[0].getUrlString())
    self.assertEqual('validated', \
                     portal.external_account_module.objectValues()[0].getValidationState())

    # invalidate career should invalidate account
    career.stop()
    self.tic()
    self.assertEqual(1, len(portal.external_account_module.objectValues()))
    self.assertEqual(person, portal.external_account_module.objectValues()[0].getSourceValue())
    self.assertEqual(person.Person_getDefaultExternalEmailText(), \
                     portal.external_account_module.objectValues()[0].getUrlString())
    self.assertEqual('invalidated', \
                     portal.external_account_module.objectValues()[0].getValidationState())

    # add a new 1 + careers then only one email account should exist
    career = person.newContent(portal_type = 'Career',
                               title = 'Career 1')
    career.start()
    self.tic()
    career = person.newContent(portal_type = 'Career',
                               title = 'Career 2')
    career.start()
    self.tic()

    self.assertEqual(1, len(portal.external_account_module.objectValues()))
    self.assertEqual(person, portal.external_account_module.objectValues()[0].getSourceValue())
    self.assertEqual(person.Person_getDefaultExternalEmailText(), \
                     portal.external_account_module.objectValues()[0].getUrlString())
    self.assertEqual('validated', \
                     portal.external_account_module.objectValues()[0].getValidationState())

    # create a person whose email is NOT managed
    portal = self.getPortal()
    person = portal.person_module.newContent(first_name = 'First',
                                             last_name = 'Last',
                                             default_email_text = 'ivan@not-managed-domain.org')
    person.validate()
    career = person.newContent(portal_type = 'Career',
                               title = 'Career 0')
    career.start()
    self.tic()
    self.assertEqual(1, len(portal.external_account_module.objectValues()))
    self.assertNotIn(person, [x.getSourceValue() for x in portal.external_account_module.objectValues()])


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestExternalAccount))
  return suite
