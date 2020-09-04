##############################################################################
# Copyright (c) 2016 Nexedi SARL and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

class PortalTypeOfPortalTypeTestCase(ERP5TypeTestCase):
  """
  Base class to test Portal Types of other Portal Types
  """
  def getBusinessTemplateList(self):
    return ('erp5_core', 'erp5_base', 'erp5_simulation', 'erp5_accounting')

  def setUpPropertyOnPortalType(self, portal_type_id, property_name, property_value):
    portal_type = self.portal.portal_types.get(portal_type_id, None)
    portal_type.setProperty(property_name, property_value)

  def cleanPropertyOnPortalType(self, portal_type_id, property_name):
    portal_type = self.portal.portal_types.get(portal_type_id, None)
    portal_type.setProperty(property_name, None)


class TestDeliveryTypeInformation(PortalTypeOfPortalTypeTestCase):
  """
  Delivery Type is a Base Type on which a list of allowed ledgers is defined.
  This suite checks that its custom features are correctly implemented.
  """

  def afterSetUp(self):
    self.createLedgerCategory()

  @UnrestrictedMethod
  def createLedgerCategory(self):
    portal_categories = self.portal.portal_categories
    ledger = self.portal.portal_categories.get('ledger', None)
    if ledger is None:
      ledger = portal_categories.newContent(portal_type='Base Category',
                                            id='ledger')

    accounting_ledger = ledger.get('accounting', None)
    if accounting_ledger is None:
      accounting_ledger = ledger.newContent(portal_type='Category',
                                            id='accounting')

    if accounting_ledger.get('general', None) is None:
      accounting_ledger.newContent(portal_type='Category', id='general')
    if accounting_ledger.get('detailed', None) is None:
      accounting_ledger.newContent(portal_type='Category', id='detailed')

  def testDefaultLedgerIsSetOnObjectIfSetOnPortalType(self):
    """
    Sets up a list of ledger on the Accounting Transaction portal type,
    which is a DeliveryTypeInformation, and checks that new Accounting Transactions
    have a default ledger set at their creation
    """
    portal_type = "Accounting Transaction"
    self.setUpPropertyOnPortalType(
        portal_type,
        "ledger_list",
        ['accounting/general', 'accounting/detailed'])

    self.assertEqual(self.portal.portal_types.get(portal_type).getDefaultLedger(),
                     'accounting/general')

    module = self.portal.getDefaultModule(portal_type)
    accounting_transaction = module.newContent(portal_type=portal_type)

    self.assertEqual(accounting_transaction.hasLedger(), True)
    self.assertEqual(accounting_transaction.getLedgerList(),
                     ['accounting/general'])

  def testDefaultLedgerIsNotSetOnObjectIfNotSetOnPortalType(self):
    """
    If no ledger is defined on the portal type, then it means the
    "allowed ledger list" feature is not in use in this instance
    """
    portal_type = "Accounting Transaction"

    portal_type_object = self.portal.portal_types.get(portal_type)
    self.cleanPropertyOnPortalType(portal_type, 'ledger')
    # No ledger should be set on the portal type
    self.assertEqual(portal_type_object.getLedgerList(), [])

    module = self.portal.getDefaultModule(portal_type)
    accounting_transaction = module.newContent(portal_type=portal_type)

    self.assertEqual(accounting_transaction.getLedgerList(), [])

  def testDefaultLedgerIsOverwrittenByNewContentParameter(self):
    """
    If a Delivery is created with a given ledger, then it should overwrite
    the default ledger
    """
    portal_type = "Accounting Transaction"
    self.setUpPropertyOnPortalType(
        portal_type,
        "ledger_list",
        ['accounting/general', 'accounting/detailed'])

    self.assertEqual(self.portal.portal_types.get(portal_type).getDefaultLedger(),
                     'accounting/general')

    module = self.portal.getDefaultModule(portal_type)
    accounting_transaction = module.newContent(portal_type=portal_type,
                                               ledger='accounting/detailed')

    self.assertEqual(accounting_transaction.hasLedger(), True)
    self.assertEqual(accounting_transaction.getLedgerList(),
                     ['accounting/detailed'])
