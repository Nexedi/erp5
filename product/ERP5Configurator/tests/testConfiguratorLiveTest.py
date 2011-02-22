##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import transaction
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
import unittest

HTTP_OK = 200
MOVED_TEMPORARILY = 302

class TestConfiguratorLiveTest(ERP5TypeTestCase):
  """ Run all live configurator tests
  """
  auth = 'manager:manager'

  def loginManager(self, quiet=0):
    """
    Most of the time, we need to login before doing anything
    """
    uf = getattr(self.getPortal(), 'acl_users', None)
    uf._doAddUser('manager', 'manager',
                  ['Manager'], [])
    user = uf.getUserById('manager').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    """
    Create ERP5 user.
    This has to be called only once.
    """
    self.loginManager()
    transaction.commit()

  def runLiveTest(self, test_name):
    """
    Run a live test
    """
    response = self.publish('/%s/portal_classes/runLiveTest?' \
                            'test_list:list=%s' % \
                    (self.portal.getId(), test_name), self.auth)

    self.assertFalse("FAILED" in response.getBody(), response.getBody())
    self.assertEquals(HTTP_OK, response.getStatus())
    self.assertTrue(response.getHeader('content-type').startswith('text/plain'))

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
        'erp5_base',
        'erp5_simulation',
        'erp5_dhtml_style',
        'erp5_jquery',
        'erp5_jquery_ui',
        'erp5_web',
        'erp5_ingestion',
        'erp5_ingestion_mysql_innodb_catalog',
        'erp5_accounting', 
        'erp5_dms', 
        'erp5_knowledge_pad',
        'erp5_pdm',
        'erp5_crm',
        'erp5_trade',
        'erp5_tax_resource', 
        'erp5_discount_resource',
        'erp5_invoicing',
        'erp5_workflow',
        'erp5_configurator',
        'erp5_configurator_standard_categories',
        'erp5_configurator_standard',)

  def test_01_standard_workflow(self):
    """
    Open Order test
    """
    return self.runLiveTest("testLiveStandardConfigurationWorkflow")

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestConfiguratorLiveTest))
  return suite

