##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#               Aurelien Calonne <aurel@nexedi.com>
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

import os
import transaction
from Products.ERP5TioSafe.tests.testTioSafeMixin import testTioSafeMixin

class testPrestashopMixin(testTioSafeMixin):
  """ This class provides the Prestashop generics elements. """

  def getBusinessTemplateList(self):
    """ Return the list of BT required by unit tests. """
    return testTioSafeMixin.getBusinessTemplateList(self) + (
      'erp5_tiosafe_prestashop',
      )

  def initPrestashopTest(self):
    """ This method is called after the SetUp method. """
    # Declare some shortcuts
    self.prestashop = self.portal.portal_integrations.prestashop
    # Path for integration site dump
    self.ps_dump_path = 'dump/prestashop'
    # Init the prestashop database
    self.loadSQLDump(
        self.portal.erp5_sql_connection,
        'dump/prestashop/dump_00_init_tables.sql',
    )
    # set the language used by prestashop
    self.prestashop.setLanguage(2)
    # Update the connection to use the PHPUnitTestConnection
    url = os.path.dirname(__file__)
    url = url.split('/ERP5TioSafe/')[0] + '/ERP5TioSafe'
    url += '/plugins/prestashop/modules/oneclickconnect'
    connection_plugin = self.getConnectionPlugin(self.prestashop)
    connection_plugin.setUrlString(url)
    connection_plugin.setTransport('php_unit_test')
    self.updateSynchronizationObjects()
    self.organisation = self.prestashop.getSourceAdministrationValue()
    self.prestashop.recursiveReindexObject()
    transaction.commit()
    self.tic()


