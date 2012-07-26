# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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
import sys

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG


class TestERP5LdapCatalog(ERP5TypeTestCase):
  """
    Tests for ERP5 Ldap Catalog.

  To setup LDAP server (on Mandriva):
  1. install openldap-clients, openldap-servers
  2. change following options in /etc/openldap/slapd.conf:
    suffix          "dc=erp5,dc=org"
    rootdn          "cn=test,dc=erp5,dc=org"
    rootpw          test
  3. (re)start ldap
  4. bootstrap with the following command from this directory :
    ldapadd -c -x -h localhost -D "cn=test,dc=erp5,dc=org" -W -f \
      bootstrap_erp5_ldap_catalog_test.ldif
  """

  def getTitle(self):
    return "ERP5 Ldap Catalog"

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_ldap_catalog',)

  # Different variables used for this test
  hostport = 'localhost:389'
  basedn = 'dc=erp5,dc=org'
  bind_as = 'cn=test,dc=erp5,dc=org'
  password = 'test'

  def getLdapConnection(self):
    return self.getPortal().erp5_ldap_connection

  def afterSetUp(self):
    self.login()
    self.getLdapConnection().manage_close()
    self.getLdapConnection().manage_edit(
            'ERP5 LDAP Test Connection',
            self.hostport,
            self.basedn,
            self.bind_as,
            self.password,
            1)
    self.commit()
    # make sure there is no message any more
    self.tic()

  def beforeTearDown(self):
    for module in [ self.getPersonModule(),
                    self.getOrganisationModule(),
                    self.getCategoryTool().region,
                    self.getCategoryTool().group ]:
      module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def test_01_HasEverything(self):
    """Test has everything
    """
    self.assertTrue(self.getCategoryTool() is not None)
    self.assertTrue(self.getTypeTool() is not None)
    self.assertTrue(self.getLdapConnection() is not None)
    self.assertTrue(self.getCatalogTool() is not None)

  def test_02_person_ldap_cataloging(self):
    """
    Test Ldap Indexation
    """
    #Create 3 Persons
    for i in xrange(3):
      self.getPersonModule().newContent(portal_type='Person',
                                        first_name='Foo%s' % i,
                                        last_name='Bar%s' % i,
                                        reference='foobar%s' % i,
                                        password='secret%s' % i,
                                        default_email_text='foo%s@bar.com' % i)
    self.tic()
    #Check Indexation
    for p in self.getPersonModule().contentValues():
      uid = p.getUid()
      result_ldap = self.getPortal().z_ldap_search_person_by_uid(uid=uid)[0]
      self.assertEqual(str(uid), result_ldap.uidNumber[0])
      self.assertEqual(p.getReference(), result_ldap.uid[0])
      #Arbitrary value needed by posixAccount Schema
      self.assertEqual('9000', result_ldap.gidNumber[0])
      self.assertEqual(p.getFirstName(), result_ldap.givenName[0])
      self.assertEqual('/home/%s' % (p.getReference()), result_ldap.homeDirectory[0])
      self.assertEqual(p.getDefaultEmailText(), result_ldap.mail[0])
      self.assertEqual(p.getLastName(), result_ldap.sn[0])
      self.assertEqual(p.getPassword(), result_ldap.userPassword[0])
    #Clear Catalog
    self.getPortal().portal_catalog.erp5_mysql_innodb.manage_catalogClear()
    self.tic()
    #Check Catalog is cleared
    self.assertEqual(len(self.getPortal().z_ldap_search_person_list()), 0)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestERP5LdapCatalog))
  return suite

