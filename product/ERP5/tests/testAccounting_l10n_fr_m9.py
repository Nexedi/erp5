##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                       Jerome Perrin <jerome@nexedi.com>
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

"""Test suite for erp5_accounting_l10n_m9
"""
import os, sys
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))

os.environ.setdefault('EVENT_LOG_FILE', 'zLOG.log')
os.environ.setdefault('EVENT_LOG_SEVERITY', '-300')

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from Products.DCWorkflow.DCWorkflow import ValidationFailed

class TestAccounting_l10n_M9(ERP5TypeTestCase):
  """Test Accounting M9 and Invoice Transmission Sheets.
  """
  RUN_ALL_TESTS = 1
  purchase_invoice_transmission_sheet_portal_type = \
        'Purchase Invoice Transmission Sheet'

  def getTitle(self):
    return "ERP5 Accounting l10n M9"
  
  def getPurchaseInvoiceTransmissionSheetModule(self):
    """Returns the module for purchase invoice transmission sheets.
    """
    return getattr( self.portal,
                    'purchase_invoice_transmission_sheet_module',
                    None )
  
  def getAccountingModule(self):
    """Returns the accounting module."""
    return getattr( self.portal, 'accounting_module', None)

  def getAccountModule(self):
    """Returns the account module."""
    return getattr( self.portal, 'account_module', None)

  def getBusinessTemplateList(self):
    return ( 'erp5_base',
             'erp5_trade', # TODO: remove those dependencies
             'erp5_pdm',
             'erp5_pdf_style',
             'erp5_accounting',
             'erp5_accounting_l10n_fr_m9',
           )

  def login(self):
    """creates a user and login"""
    uf = self.getPortal().acl_users
    uf._doAddUser('zope', 'zope', ['Member', 'Assignee', 'Assignor',
                               'Auditor', 'Author', 'Manager'], [])
    user = uf.getUserById('zope').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self):
    """set up """
    self.login()
    portal = self.getPortal()
    self.portal = portal
    self.category_tool = portal.portal_categories
    self.section = self._createOrganisation()
    self.mirror_section = self._createOrganisation()

  def _createOrganisation(self, **kw):
    """Create an organisation and index it.
    """
    org = self.getOrganisationModule().newContent(portal_type='Organisation')
    org.edit(**kw)
    get_transaction().commit()
    self.tic()
    return org

  def _getAccount(self, account_id, **kw):
    """Get an account or create it.
    """
    account_module = self.getAccountModule()
    account = getattr(account_module, account_id, None)
    if account is None:
      account = account_module.newContent(id=account_id)
    account.edit(**kw)
    get_transaction().commit()
    self.tic()
    return account

  def _createPurchaseInvoice(self, amount=100, **kw):
    """Create a purchase invoice and index it.
    """
    payable_account = self._getAccount('payable_account',
                                       gap='fr/m9/4/40/401/4012',
                                       account_type='liability/payable')
    expense_account = self._getAccount('expense_account',
                                       gap='fr/m9/6/60/602/6022/60225',
                                       account_type='expense')
    invoice = self.getAccountingModule().newContent(
                      portal_type='Purchase Invoice Transaction',
                      created_by_builder=1)
    invoice.newContent(portal_type='Accounting Transaction Line',
                       source_value=expense_account,
                       quantity=amount)
    invoice.newContent(portal_type='Accounting Transaction Line',
                       source_value=payable_account,
                       quantity=-amount)
    invoice.edit(**kw)
    get_transaction().commit()
    self.tic()
    return invoice
  
  def test_TransmissionSheetModule(self):
    """Checks the purchase invoice transmission sheet module is installed."""
    self.assertNotEquals(None, self.getPurchaseInvoiceTransmissionSheetModule())
  
  def test_AccountingPlanInstallation(self):
    """Tests that the accounting plan is well installed."""
    self.failUnless('m9' in self.category_tool.gap.fr.objectIds())
    self.assertNotEquals(0, len(self.category_tool.gap.fr.m9.objectIds()))
    self.failUnless('gap/fr/m9' in [x[1] for x in
           self.portal.account_module.AccountModule_getAvailableGapList()])

  def test_SimpleTransmissionSheet(self):
    """Simple use case for a transmission sheet."""
    invoice = self._createPurchaseInvoice(
                            destination_section_value=self.section,
                            source_section_value=self.mirror_section, )
    transmission_sheet_module = self.getPurchaseInvoiceTransmissionSheetModule()
    transmission_sheet = transmission_sheet_module.newContent(
            portal_type=self.purchase_invoice_transmission_sheet_portal_type)
    self.assertEquals(transmission_sheet.getValidationState(), 'draft')
    # add an invoice to the transamission sheet
    invoice.setAggregateValue(transmission_sheet)
    invoice.recursiveImmediateReindexObject()
    self.getWorkflowTool().doActionFor(
                            transmission_sheet,
                            'emit_action')
    self.assertEquals(transmission_sheet.getValidationState(),
                            'emitted')

  def test_TransmissionSheetEmitRefusedIfNoInvoice(self):
    """Transmission sheet cannot be emitted if it doesn't contain any invoice.
    """
    transmission_sheet_module = self.getPurchaseInvoiceTransmissionSheetModule()
    transmission_sheet = transmission_sheet_module.newContent(
            portal_type=self.purchase_invoice_transmission_sheet_portal_type)
    self.assertEquals(transmission_sheet.getValidationState(), 'draft')
    self.assertRaises(ValidationFailed, self.getWorkflowTool().doActionFor,
                      transmission_sheet, 'emit_action')

if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAccounting_l10n_M9))
    return suite

