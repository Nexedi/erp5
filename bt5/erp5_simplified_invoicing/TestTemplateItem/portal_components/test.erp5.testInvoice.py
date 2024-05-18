##############################################################################
#
# Copyright (c) 2004-2008 Nexedi SA and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#          Jerome Perrin <jerome@nexedi.com>
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
"""
  Tests invoice creation from simulation.

"""
from __future__ import print_function
import xml.dom.minidom
import zipfile

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import FileUpload
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5OOo.OOoUtils import OOoParser
from DateTime import DateTime
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testPackingList import TestPackingListMixin
from Products.ERP5.tests.utils import newSimulationExpectedFailure
from erp5.component.module.TestInvoiceMixin import TestInvoiceMixin, TestSaleInvoiceMixin


class TestInvoice(TestInvoiceMixin):
  """Test methods for sale and purchase invoice.
  Subclasses must defines portal types to use.
  """
  trade_condition_portal_type = 'Sale Trade Condition'
  quiet = 1
  def test_invoice_transaction_line_resource(self):
    """
    tests that simulation movements corresponding to accounting line have a
    good resource in the simulation
    """
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency',
                                base_unit_quantity=0.01)
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            price_currency= currency.getRelativeUrl(),
                            default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            price_currency= currency.getRelativeUrl(),
                            default_address_region=self.default_region)
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')
    order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                                  quantity=1,
                                  price=2)

    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()

    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    order_movement = related_applied_rule.contentValues()[0]
    delivery_applied_rule = order_movement.contentValues()[0]
    delivery_movement = delivery_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = [x for x in invoice_movement.contentValues() \
                                        if x.getSpecialiseReference() == 'default_invoice_transaction_rule'][0]
    invoice_transaction_movement =\
         invoice_transaction_applied_rule.contentValues()[0]
    self.assertEqual(currency,
          invoice_transaction_movement.getResourceValue())
    self.assertEqual(currency,
          delivery_movement.getPriceCurrencyValue())

  @newSimulationExpectedFailure
  def test_modify_planned_order_invoicing_rule(self):
    """
    tests that modifying a planned order affects movements from invoicing
    rule
    """
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency',
                                base_unit_quantity=0.01)

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            price_currency= currency.getRelativeUrl())
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            price_currency= currency.getRelativeUrl())
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                                  quantity=1,
                                  price=2)

    other_entity = self.portal.organisation_module.newContent(
                                    portal_type='Organisation',
                                    title='Other Entity',
                                    price_currency=currency.getRelativeUrl())
    other_project = self.portal.project_module.newContent(
                                    portal_type='Project',
                                    title='Other Project')
    order.plan()
    self.tic()
    self.assertEqual('planned', order.getSimulationState())

    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    delivery_movement = related_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]

    order_line.setSourceValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                      invoice_movement.getSourceValue())

    order_line.setDestinationValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                      invoice_movement.getDestinationValue())

    order_line.setSourceSectionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                      invoice_movement.getSourceSectionValue())

    # make sure destination_section != source_section, this might be needed by
    # some rules
    order_line.setSourceSectionValue(order_line.getDestinationSectionValue())

    order_line.setDestinationSectionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getDestinationSectionValue())

    order_line.setSourceAdministrationValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getSourceAdministrationValue())

    order_line.setDestinationAdministrationValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
            invoice_movement.getDestinationAdministrationValue())

    order_line.setSourceDecisionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getSourceDecisionValue())

    order_line.setDestinationDecisionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
            invoice_movement.getDestinationDecisionValue())

    order_line.setSourceProjectValue(other_project)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_project,
                 invoice_movement.getSourceProjectValue())

    order_line.setDestinationProjectValue(other_project)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_project,
            invoice_movement.getDestinationProjectValue())

    order_line.setSourcePaymentValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getSourcePaymentValue())

    order_line.setDestinationPaymentValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
            invoice_movement.getDestinationPaymentValue())

    order_line.setSourceFunctionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
                 invoice_movement.getSourceFunctionValue())

    order_line.setDestinationFunctionValue(other_entity)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_entity,
            invoice_movement.getDestinationFunctionValue())

    self.assertNotEqual(123, order_line.getPrice())
    order_line.setPrice(123)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(123,
            invoice_movement.getPrice())

    self.assertNotEqual(456, order_line.getQuantity())
    order_line.setQuantity(456)
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(456,
            invoice_movement.getQuantity())

    other_resource = self.portal.product_module.newContent(
                                        portal_type='Product',
                                        title='Other Resource')
    order_line.setResourceValue(other_resource)
    self.tic()
    # after changing 'resource', related simulation movement will be
    # replaced with another id, and we need to find the appropriate one
    # here.
    delivery_movement = related_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(other_resource,
            invoice_movement.getResourceValue())

    order_line.setStartDate(DateTime(2001, 2, 3))
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(DateTime(2001, 2, 3),
                 invoice_movement.getStartDate())

    order_line.setStopDate(DateTime(2002, 3, 4))
    self.tic()
    invoice_movement = invoice_applied_rule.contentValues()[0]
    self.assertEqual(DateTime(2002, 3, 4),
                 invoice_movement.getStopDate())

  @newSimulationExpectedFailure
  def test_modify_planned_order_invoice_transaction_rule(self):
    """
    tests that modifying a planned order affects movements from invoice
    transaction rule
    """
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency',
                                base_unit_quantity=0.01)
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            default_address_region=self.default_region)
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')
    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                                  quantity=1,
                                  price=2)
    other_entity = self.portal.organisation_module.newContent(
                                      portal_type='Organisation',
                                      title='Other Entity',
                                      default_address_region=self.default_region)
    other_project = self.portal.project_module.newContent(
                                      portal_type='Project',
                                      title='Other Project')
    order.plan()
    self.tic()
    self.assertEqual('planned', order.getSimulationState())

    related_applied_rule = order.getCausalityRelatedValue(
                             portal_type='Applied Rule')
    order_movement = related_applied_rule.contentValues()[0]
    delivery_applied_rule = order_movement.contentValues()[0]
    delivery_movement = delivery_applied_rule.contentValues()[0]
    invoice_applied_rule = delivery_movement.contentValues()[0]
    invoice_movement = invoice_applied_rule.contentValues()[0]
    invoice_transaction_applied_rule = [x for x in invoice_movement.contentValues() \
                                        if x.getSpecialiseReference() == 'default_invoice_transaction_rule'][0]

    # utility function to return the simulation movement that should be used
    # for "income" line
    def getIncomeSimulationMovement(applied_rule):
      for movement in applied_rule.contentValues():
        if movement.getDestination() == 'account_module/purchase'\
            and movement.getSource() == 'account_module/sale':
          return movement
      self.fail('Income movement not found')

    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)

    order_line.setSourceSectionValue(other_entity)
    self.tic()
    self.assertEqual(other_entity,
                      invoice_transaction_movement.getSourceSectionValue())

    # make sure destination_section != source_section, this might be needed by
    # some rules
    order_line.setSourceSectionValue(order_line.getDestinationSectionValue())

    order_line.setDestinationSectionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getDestinationSectionValue())

    order_line.setSourceAdministrationValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getSourceAdministrationValue())

    order_line.setDestinationAdministrationValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
            invoice_transaction_movement.getDestinationAdministrationValue())

    order_line.setSourceDecisionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getSourceDecisionValue())

    order_line.setDestinationDecisionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
            invoice_transaction_movement.getDestinationDecisionValue())

    order_line.setSourceProjectValue(other_project)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_project,
                 invoice_transaction_movement.getSourceProjectValue())

    order_line.setDestinationProjectValue(other_project)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_project,
            invoice_transaction_movement.getDestinationProjectValue())

    order_line.setSourceFunctionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getSourceFunctionValue())

    order_line.setDestinationFunctionValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
            invoice_transaction_movement.getDestinationFunctionValue())

    order_line.setSourcePaymentValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
                 invoice_transaction_movement.getSourcePaymentValue())

    order_line.setDestinationPaymentValue(other_entity)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(other_entity,
            invoice_transaction_movement.getDestinationPaymentValue())

    order_line.setQuantity(1)
    order_line.setPrice(123)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(123,
            invoice_transaction_movement.getQuantity())

    order_line.setQuantity(456)
    order_line.setPrice(1)
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(456,
            invoice_transaction_movement.getQuantity())

    order_line.setStartDate(DateTime(2001, 2, 3))
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(DateTime(2001, 2, 3),
                 invoice_transaction_movement.getStartDate())

    order_line.setStopDate(DateTime(2002, 3, 4))
    self.tic()
    self.assertEqual(3, len(invoice_transaction_applied_rule))
    invoice_transaction_movement = getIncomeSimulationMovement(
                                        invoice_transaction_applied_rule)
    self.assertEqual(DateTime(2002, 3, 4),
                 invoice_transaction_movement.getStopDate())

  def test_Invoice_viewAsODT(self):
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    resource_tax = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource Tax',)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    invoice = self.portal.getDefaultModule(self.invoice_portal_type).newContent(
                              portal_type=self.invoice_portal_type,
                              start_date=DateTime(2008, 12, 31),
                              title='Invoice',
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            base_contribution='base_amount/tax1',
                            price=3)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=20,
                            base_contribution='base_amount/tax1',
                            price=5)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=60,
                            base_contribution='base_amount/tax2',
                            price=5)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=60,
                            price=3)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=7,
                            price=20)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource_tax,
                            use='trade/tax',
                            base_contribution='base_amount/tax1',
                            quantity=130,
                            price=0.2)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource_tax,
                            use='trade/tax',
                            base_contribution='base_amount/tax2',
                            quantity=300,
                            price=0.05)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource_tax,
                            use='trade/tax',
                            base_contribution='base_amount/tax3',
                            quantity=20,
                            price=0.1)
    invoice.confirm()
    self.tic()
    odt = invoice.Invoice_viewAsODT()
    from io import BytesIO
    output = BytesIO()
    output.write(odt)
    m = OpenDocumentTextFile(output)
    text_content=m.toString().encode('ascii','replace').decode()
    if text_content.find('Resource Tax') != -1 :
      self.fail('fail to delete the tax line in product line')
    if text_content.find('Tax Code') == -1 :
      self.fail('fail to add the tax code')
    if text_content.find('Amount') == -1 :
      self.fail('fail to add the amount for each tax')
    if text_content.find('Rate') == -1 :
      self.fail('fail to add the Rate for each tax')
    tax1_product_total_price=str(10*3+20*5)
    if text_content.find(tax1_product_total_price) == -1 :
      self.fail('fail to get the total price of products which tax1')
    tax2_product_total_price=str(60*5)
    if text_content.find(tax2_product_total_price) == -1 :
      self.fail('fail to get the total price of products which tax2')
    no_tax_product_total_price=str(60*3+7*20)
    if text_content.find(no_tax_product_total_price) == -1 :
      self.fail('fail to get the total price of products which have no tax')
    product_total_price_no_tax=str(10*3+20*5+60*5+60*3+7*20)
    if text_content.find(product_total_price_no_tax) == -1 :
      self.fail('fail to get the total price of the products without tax')
    product_total_price=str(10*3+20*5+60*5+60*3+7*20+130*0.2+300*0.05+20*0.1)
    if text_content.find(product_total_price) == -1 :
      self.fail('fail to get the total price of the products with tax')
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  def test_Invoice_viewAsODT_empty_image(self):
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    client.newContent(portal_type='Embedded File',
                      id='default_image')
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    vendor_logo = vendor.newContent(portal_type='Embedded File',
                                    id='default_image')
    self.assertEqual(0, vendor_logo.getSize())
    self.assertEqual(0, vendor.getDefaultImageWidth())
    self.assertEqual(0, vendor.getDefaultImageHeight())
    invoice = self.portal.getDefaultModule(self.invoice_portal_type).newContent(
                              portal_type=self.invoice_portal_type,
                              start_date=DateTime(2008, 12, 31),
                              title='Invoice',
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    invoice.confirm()
    self.tic()

    odt = invoice.Invoice_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

    # the <draw:image> should not be present, because there's no logo
    parser = OOoParser()
    parser.openFromBytes(odt)
    style_xml = parser.oo_files['styles.xml']
    self.assertNotIn(b'<draw:image', style_xml)

  def test_Invoice_viewAsODT_invalid_image(self):
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    import Products.ERP5Type
    file_data = FileUpload(Products.ERP5Type.__file__)
    client = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Client')
    client.newContent(portal_type='Embedded File',
                                    id='default_image',
                                    file=file_data)
    vendor = self.portal.organisation_module.newContent(
                              portal_type='Organisation', title='Vendor')
    vendor.newContent(portal_type='Embedded File',
                                    id='default_image',
                                    file=file_data)

    # width and height of an invalid image are -1 according to
    # OFS.Image.getImageInfo maybe this is not what we want here ?
    self.assertEqual(-1, vendor.getDefaultImageWidth())
    self.assertEqual(-1, vendor.getDefaultImageHeight())

    invoice = self.portal.getDefaultModule(self.invoice_portal_type).newContent(
                              portal_type=self.invoice_portal_type,
                              start_date=DateTime(2008, 12, 31),
                              title='Invoice',
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client)
    invoice.newContent(portal_type=self.invoice_line_portal_type,
                            resource_value=resource,
                            quantity=10,
                            price=3)
    invoice.confirm()
    self.tic()

    odt = invoice.Invoice_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  def test_Invoice_viewAsODT_date_before_1900(self):
    # Regression test for invoices with a date before 1900, which
    # python-2.7's strftime does not support.
    resource = self.portal.getDefaultModule(
        self.resource_portal_type
    ).newContent(
        portal_type=self.resource_portal_type,
        title='Resource',)
    client = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        title='Client')
    vendor = self.portal.organisation_module.newContent(
        portal_type='Organisation',
        title='Vendor')

    invoice = self.portal.getDefaultModule(
        self.invoice_portal_type
    ).newContent(
        portal_type=self.invoice_portal_type,
        start_date=DateTime(102, 12, 31),
        stop_date=DateTime(103, 12, 31),
        title='Invoice',
        specialise=self.business_process,
        source_value=vendor,
        source_section_value=vendor,
        destination_value=client,
        destination_section_value=client)
    invoice.newContent(
        portal_type=self.invoice_line_portal_type,
        resource_value=resource,
        quantity=10,
        price=3)
    invoice.confirm()
    self.tic()

    data_dict = invoice.Invoice_getODTDataDict()
    self.assertEqual('0102/12/31', data_dict['start_date'])
    self.assertEqual('0103/12/31', data_dict['stop_date'])
    # rendering is valid odf
    odt = invoice.Invoice_viewAsODT()
    from Products.ERP5OOo.tests.utils import Validator
    odf_validator = Validator()
    err_list = odf_validator.validate(odt)
    if err_list:
      self.fail(''.join(err_list))

  def test_invoice_building_with_cells(self):
    # if the order has cells, the invoice built from that order must have
    # cells too
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    variation_base_category_list=['size'])
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency')

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')

    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,)
    order_line.setVariationBaseCategoryList(('size', ))
    order_line.setVariationCategoryList(['size/Baby', 'size/Child/32'])
    order_line.updateCellRange()

    cell_baby = order_line.newCell('size/Baby', base_id='movement',
                             portal_type=self.order_cell_portal_type)
    cell_baby.edit(quantity=10,
                   price=4,
                   variation_category_list=['size/Baby'],
                   mapped_value_property_list=['quantity', 'price'],)

    cell_child_32 = order_line.newCell('size/Child/32', base_id='movement',
                                 portal_type=self.order_cell_portal_type)
    cell_child_32.edit(quantity=20,
                       price=5,
                       variation_category_list=['size/Child/32'],
                       mapped_value_property_list=['quantity', 'price'],)
    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()

    related_packing_list = order.getCausalityRelatedValue(
                                  portal_type=self.packing_list_portal_type)
    self.assertNotEqual(related_packing_list, None)

    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    related_invoice = related_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEqual(related_invoice, None)

    line_list = related_invoice.contentValues(
                     portal_type=self.invoice_line_portal_type)
    self.assertEqual(1, len(line_list))
    invoice_line = line_list[0]

    self.assertEqual(resource, invoice_line.getResourceValue())
    self.assertEqual(['size'], invoice_line.getVariationBaseCategoryList())
    self.assertEqual(2,
          len(invoice_line.getCellValueList(base_id='movement')))

    cell_baby = invoice_line.getCell('size/Baby', base_id='movement')
    self.assertNotEqual(cell_baby, None)
    self.assertEqual(resource, cell_baby.getResourceValue())
    self.assertEqual(10, cell_baby.getQuantity())
    self.assertEqual(4, cell_baby.getPrice())
    self.assertIn('size/Baby',
                    cell_baby.getVariationCategoryList())
    self.assertTrue(cell_baby.isMemberOf('size/Baby'))

    cell_child_32 = invoice_line.getCell('size/Child/32', base_id='movement')
    self.assertNotEqual(cell_child_32, None)
    self.assertEqual(resource, cell_child_32.getResourceValue())
    self.assertEqual(20, cell_child_32.getQuantity())
    self.assertEqual(5, cell_child_32.getPrice())
    self.assertIn('size/Child/32',
                    cell_child_32.getVariationCategoryList())
    self.assertTrue(cell_child_32.isMemberOf('size/Child/32'))



  def test_invoice_created_from_packing_list_with_no_order(self):
    # if the order has cells and an aggregate, the invoice built
    #from that order must have
    # cells too
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    variation_base_category_list=['size'])
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency')

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor')
    no_order_packing_list = \
self.portal.getDefaultModule(self.packing_list_portal_type).newContent(
                              portal_type=self.packing_list_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')

    packing_list_line = no_order_packing_list.newContent(
                        portal_type=self.packing_list_line_portal_type,
                                  resource_value=resource,)
    packing_list_line.setVariationBaseCategoryList(('size', ))
    packing_list_line.setVariationCategoryList(['size/Baby', 'size/Child/32'])
    packing_list_line.updateCellRange()

    cell_baby = packing_list_line.newCell('size/Baby', base_id='movement',
                             portal_type=self.packing_list_cell_portal_type)
    cell_baby.edit(quantity=10,
                   price=4,
                   variation_category_list=['size/Baby'],
                   mapped_value_property_list=['quantity', 'price'],)

    cell_child_32 = packing_list_line.newCell(
                                'size/Child/32',base_id='movement',
                                 portal_type=self.packing_list_cell_portal_type)
    cell_child_32.edit(quantity=20,
                       price=5,
                       variation_category_list=['size/Child/32'],
                       mapped_value_property_list=['quantity', 'price'],)
    no_order_packing_list.confirm()
    self.tic()
    self.assertNotEqual(no_order_packing_list, None)

    no_order_packing_list.start()
    no_order_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    related_invoice = no_order_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEqual(related_invoice, None)

    line_list = related_invoice.contentValues(
                     portal_type=self.invoice_line_portal_type)
    self.assertEqual(1, len(line_list))
    invoice_line = line_list[0]

    self.assertEqual(resource, invoice_line.getResourceValue())
    self.assertEqual(['size'], invoice_line.getVariationBaseCategoryList())
    self.assertEqual(2,
          len(invoice_line.getCellValueList(base_id='movement')))

    cell_baby = invoice_line.getCell('size/Baby', base_id='movement')
    self.assertNotEqual(cell_baby, None)
    self.assertEqual(resource, cell_baby.getResourceValue())
    self.assertEqual(10, cell_baby.getQuantity())
    self.assertEqual(4, cell_baby.getPrice())
    self.assertIn('size/Baby',
                    cell_baby.getVariationCategoryList())
    self.assertTrue(cell_baby.isMemberOf('size/Baby'))

    cell_child_32 = invoice_line.getCell('size/Child/32', base_id='movement')
    self.assertNotEqual(cell_child_32, None)
    self.assertEqual(resource, cell_child_32.getResourceValue())
    self.assertEqual(20, cell_child_32.getQuantity())
    self.assertEqual(5, cell_child_32.getPrice())
    self.assertIn('size/Child/32',
                    cell_child_32.getVariationCategoryList())
    self.assertTrue(cell_child_32.isMemberOf('size/Child/32'))

  def test_invoice_building_with_cells_and_aggregate(self):
    # if the order has cells and an aggregate, the invoice built
    #from that order must have
    # cells too
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    variation_base_category_list=['size'])
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency')

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')

    order_line = order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,)
    order_line.setVariationBaseCategoryList(('size', ))
    order_line.setVariationCategoryList(['size/Baby', 'size/Child/32'])
    order_line.updateCellRange()

    cell_baby = order_line.newCell('size/Baby', base_id='movement',
                             portal_type=self.order_cell_portal_type)
    cell_baby.edit(quantity=10,
                   price=4,
                   variation_category_list=['size/Baby'],
                   mapped_value_property_list=['quantity', 'price'],)

    cell_child_32 = order_line.newCell('size/Child/32', base_id='movement',
                                 portal_type=self.order_cell_portal_type)
    cell_child_32.edit(quantity=20,
                       price=5,
                       variation_category_list=['size/Child/32'],
                       mapped_value_property_list=['quantity', 'price'],)
    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()

    related_packing_list = order.getCausalityRelatedValue(
                                  portal_type=self.packing_list_portal_type)
    self.assertNotEqual(related_packing_list, None)

    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    related_invoice = related_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEqual(related_invoice, None)

    line_list = related_invoice.contentValues(
                     portal_type=self.invoice_line_portal_type)
    self.assertEqual(1, len(line_list))
    invoice_line = line_list[0]

    self.assertEqual(resource, invoice_line.getResourceValue())
    self.assertEqual(['size'], invoice_line.getVariationBaseCategoryList())
    self.assertEqual(2,
          len(invoice_line.getCellValueList(base_id='movement')))

    cell_baby = invoice_line.getCell('size/Baby', base_id='movement')
    self.assertNotEqual(cell_baby, None)
    self.assertEqual(resource, cell_baby.getResourceValue())
    self.assertEqual(10, cell_baby.getQuantity())
    self.assertEqual(4, cell_baby.getPrice())
    self.assertIn('size/Baby',
                    cell_baby.getVariationCategoryList())
    self.assertTrue(cell_baby.isMemberOf('size/Baby'))

    cell_child_32 = invoice_line.getCell('size/Child/32', base_id='movement')
    self.assertNotEqual(cell_child_32, None)
    self.assertEqual(resource, cell_child_32.getResourceValue())
    self.assertEqual(20, cell_child_32.getQuantity())
    self.assertEqual(5, cell_child_32.getPrice())
    self.assertIn('size/Child/32',
                    cell_child_32.getVariationCategoryList())
    self.assertTrue(cell_child_32.isMemberOf('size/Child/32'))


  def test_description_copied_on_lines(self):
    # if the order lines have different descriptions, description must be
    # copied in the simulation and on created movements
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',)
    resource2 = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource2',)
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='Currency')

    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor')
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008, 1, 1),
                              price_currency_value=currency,
                              title='Order')

    order.newContent(portal_type=self.order_line_portal_type,
                                  quantity=3,
                                  price=10,
                                  description='The first line',
                                  resource_value=resource,)
    order.newContent(portal_type=self.order_line_portal_type,
                                  quantity=5,
                                  price=10,
                                  description='The second line',
                                  resource_value=resource2,)

    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()

    related_packing_list = order.getCausalityRelatedValue(
                                  portal_type=self.packing_list_portal_type)
    self.assertNotEqual(related_packing_list, None)

    movement_list = related_packing_list.getMovementList()
    self.assertEqual(2, len(movement_list))
    self.assertEqual(['The first line'],
        [m.getDescription() for m in movement_list if m.getQuantity() == 3])
    self.assertEqual(['The second line'],
        [m.getDescription() for m in movement_list if m.getQuantity() == 5])

    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    related_invoice = related_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEqual(related_invoice, None)

    movement_list = related_invoice.getMovementList(
                              portal_type=self.invoice_line_portal_type)
    self.assertEqual(2, len(movement_list))
    self.assertEqual(['The first line'],
        [m.getDescription() for m in movement_list if m.getQuantity() == 3])
    self.assertEqual(['The second line'],
        [m.getDescription() for m in movement_list if m.getQuantity() == 5])


  def test_CopyAndPaste(self):
    """Test copy on paste on Invoice.
    When an invoice is copy/pasted, references should be resetted.
    """
    accounting_module = self.portal.accounting_module
    invoice = accounting_module.newContent(
                    portal_type=self.invoice_portal_type)
    invoice.edit(reference='reference',
                 source_reference='source_reference',
                 destination_reference='destination_reference',)
    cb_data = accounting_module.manage_copyObjects([invoice.getId()])
    copied, = accounting_module.manage_pasteObjects(cb_data)
    new_invoice = accounting_module[copied['new_id']]
    self.assertNotEqual(invoice.getReference(),
                         new_invoice.getReference())
    self.assertNotEqual(invoice.getSourceReference(),
                         new_invoice.getSourceReference())
    self.assertNotEqual(invoice.getDestinationReference(),
                         new_invoice.getDestinationReference())

  def test_delivery_mode_and_incoterm_on_invoice(self):
    """
    test that categories delivery_mode and incoterm are copied on
    the invoice by the delivery builder
    """
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
                    product_line='apparel')
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    self.tic()#execute transaction
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            default_address_region=self.default_region)
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              delivery_mode=self.mail_delivery_mode,
                              incoterm=self.cpt_incoterm,
                              title='Order')
    order.newContent(portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                                  quantity=5,
                                  price=2)
    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type=self.packing_list_portal_type)
    self.assertNotEqual(related_packing_list, None)
    self.assertEqual(related_packing_list.getDeliveryMode(),
                         order.getDeliveryMode())
    self.assertEqual(related_packing_list.getIncoterm(),
                         order.getIncoterm())
    related_packing_list.start()
    related_packing_list.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()
    related_invoice = related_packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEqual(related_invoice, None)
    self.assertEqual(related_invoice.getDeliveryMode(),
                         order.getDeliveryMode())
    self.assertEqual(related_invoice.getIncoterm(),
                         order.getIncoterm())


  def test_01_quantity_unit_copied(self):
    """
    tests that when a resource uses different quantity unit that the
    quantity units are copied on the packing list line and then the invoice
    line using the delivery builers
    """
    resource = self.portal.product_module.newContent(
                    portal_type='Product',
                    title='Resource',
                    product_line='apparel')
    resource.setQuantityUnitList([self.unit_piece_quantity_unit,
                                 self.mass_quantity_unit])
    currency = self.portal.currency_module.newContent(
                                portal_type='Currency',
                                title='euro')
    currency.setBaseUnitQuantity(0.01)
    self.tic()#execute transaction
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client',
                            default_address_region=self.default_region)
    vendor = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Vendor',
                            default_address_region=self.default_region)
    order = self.portal.getDefaultModule(self.order_portal_type).newContent(
                              portal_type=self.order_portal_type,
                              specialise=self.business_process,
                              source_value=vendor,
                              source_section_value=vendor,
                              destination_value=client,
                              destination_section_value=client,
                              start_date=DateTime(2008,10, 21),
                              price_currency_value=currency,
                              delivery_mode=self.mail_delivery_mode,
                              incoterm=self.cpt_incoterm,
                              title='Order')
    first_order_line = order.newContent(
                          portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                             quantity_unit = self.unit_piece_quantity_unit,
                                  quantity=5,
                                  price=3)
    second_order_line = order.newContent(
                          portal_type=self.order_line_portal_type,
                                  resource_value=resource,
                             quantity_unit=self.mass_quantity_unit,
                                  quantity=1.5,
                                  price=2)
    self.assertEqual(first_order_line.getQuantityUnit(),
                      self.unit_piece_quantity_unit)
    self.assertEqual(second_order_line.getQuantityUnit(),
                      self.mass_quantity_unit)

    order.confirm()
    self.tic()
    self.stepPackingListBuilderAlarm()
    self.tic()
    related_packing_list = order.getCausalityRelatedValue(
                                portal_type=self.packing_list_portal_type)
    self.assertNotEqual(related_packing_list, None)
    movement_list = related_packing_list.getMovementList()
    self.assertEqual(len(movement_list),2)
    movement_list = sorted(movement_list, key=lambda x: x.getQuantity())
    self.assertEqual(movement_list[0].getQuantityUnit(),
                      self.mass_quantity_unit)
    self.assertEqual(movement_list[0].getQuantity(), 1.5)
    self.assertEqual(movement_list[1].getQuantityUnit(),
                      self.unit_piece_quantity_unit)
    self.assertEqual(movement_list[1].getQuantity(), 5)

    related_packing_list.start()
    related_packing_list.stop()
    related_packing_list.deliver()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()
    related_invoice = related_packing_list.getCausalityRelatedValue(
                                portal_type=self.invoice_portal_type)
    self.assertNotEqual(related_invoice, None)
    movement_list = related_invoice.getMovementList()
    self.assertEqual(len(movement_list),2)
    movement_list = sorted(movement_list, key=lambda x: x.getQuantity())
    self.assertEqual(movement_list[0].getQuantityUnit(),
                      self.mass_quantity_unit)
    self.assertEqual(movement_list[0].getQuantity(), 1.5)
    self.assertEqual(movement_list[1].getQuantityUnit(),
                      self.unit_piece_quantity_unit)
    self.assertEqual(movement_list[1].getQuantity(), 5)



  def _acceptDivergenceOnInvoice(self, invoice, divergence_list):
    print(invoice, divergence_list)
    self._solveDivergence(invoice, 'quantity', 'Accept Solver')

  def test_accept_quantity_divergence_on_invoice_with_stopped_packing_list(
                self, quiet=quiet):
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.PACKING_LIST_DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    packing_list = sequence.get('packing_list')
    packing_list.setReady()
    packing_list.start()
    packing_list.stop()
    self.assertEqual('stopped', packing_list.getSimulationState())
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    invoice = packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEqual(invoice, None)
    invoice_line_list = invoice.getMovementList()
    self.assertEqual(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]

    new_quantity = invoice_line.getQuantity() * 2
    invoice_line.setQuantity(new_quantity)

    self.tic()

    self.assertTrue(invoice.isDivergent())
    divergence_list = invoice.getDivergenceList()
    self.assertEqual(1, len(divergence_list))

    divergence = divergence_list[0]
    self.assertEqual('quantity', divergence.tested_property)

    # accept decision
    self._acceptDivergenceOnInvoice(invoice, divergence_list)

    self.tic()
    self.assertEqual('solved', invoice.getCausalityState())

    self.assertEqual([], invoice.getDivergenceList())
    self.assertEqual(new_quantity, invoice_line.getQuantity())
    self.assertEqual(new_quantity,
          invoice_line.getDeliveryRelatedValue(portal_type='Simulation Movement'
              ).getQuantity())

    self.assertEqual([], packing_list.getDivergenceList())
    self.assertEqual('solved', packing_list.getCausalityState())

  def _adoptDivergenceOnInvoice(self, invoice, divergence_list):
    print(invoice, divergence_list)
    self._solveDivergence(invoice, 'quantity', 'Adopt Solver')

  def test_adopt_quantity_divergence_on_invoice_line_with_stopped_packing_list(
                self, quiet=quiet):
    # #1053
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.PACKING_LIST_DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list.getMovementList()[0]
    previous_quantity = packing_list_line.getQuantity()
    previous_resource = packing_list_line.getResource()
    previous_price = packing_list_line.getPrice()

    packing_list.setReady()
    packing_list.start()
    packing_list.stop()
    self.assertEqual('stopped', packing_list.getSimulationState())
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    invoice = packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEqual(invoice, None)
    invoice_line_list = invoice.getMovementList()
    self.assertEqual(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]

    new_quantity = invoice_line.getQuantity() * 2
    invoice_line.setQuantity(new_quantity)

    self.tic()

    self.assertTrue(invoice.isDivergent())
    divergence_list = invoice.getDivergenceList()
    self.assertEqual(1, len(divergence_list))

    divergence = divergence_list[0]
    self.assertEqual('quantity', divergence.tested_property)

    # adopt prevision
    self._adoptDivergenceOnInvoice(invoice, divergence_list)

    self.tic()
    self.assertEqual([], invoice.getDivergenceList())
    self.assertEqual('solved', invoice.getCausalityState())

    self.assertEqual(1,
        len(invoice.getMovementList(portal_type=self.invoice_line_portal_type)))
    self.assertEqual(0,
        len(invoice.getMovementList(portal_type=self.invoice_transaction_line_portal_type)))

    self.assertEqual(previous_resource, invoice_line.getResource())
    self.assertEqual(previous_quantity, invoice_line.getQuantity())
    self.assertEqual(previous_price, invoice_line.getPrice())
    self.assertEqual(previous_quantity,
          invoice_line.getDeliveryRelatedValue(portal_type='Simulation Movement'
              ).getQuantity())

    self.assertEqual([], packing_list.getDivergenceList())
    self.assertEqual('solved', packing_list.getCausalityState())

  def test_merge_accounting_invoice(
                self, quiet=quiet):
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.PACKING_LIST_DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    packing_list = sequence.get('packing_list')
    packing_list_line = packing_list.getMovementList()[0]
    quantity = packing_list_line.getQuantity()
    resource = packing_list_line.getResource()
    price = packing_list_line.getPrice()
    packing_list.setReady()
    packing_list.start()
    packing_list.stop()
    self.tic()
    self.default_quantity = self.default_quantity + 10
    self.default_price = self.default_price + 10
    self.tic()
    sequence_list.play(self, quiet=quiet)
    packing_list_2 = sequence.get('packing_list')
    packing_list_line = packing_list_2.getMovementList()[0]
    quantity_2 = packing_list_line.getQuantity()
    resource_2 = packing_list_line.getResource()
    price_2 = packing_list_line.getPrice()
    packing_list_2.setReady()
    packing_list_2.start()
    packing_list_2.stop()
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()
    self.default_quantity = self.default_quantity - 10
    self.default_price = self.default_price - 10

    invoice = packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    invoice_2 = packing_list_2.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEqual(invoice, None)
    self.assertNotEqual(invoice_2, None)
    self.tic()
    error_list = self.portal.portal_simulation.mergeDeliveryList([invoice, invoice_2])
    self.tic()
    self.assertEqual(0, len(error_list))
    self.assertEqual(invoice.getSimulationState(), 'confirmed')
    # MergeDeliveryList change the first delivery to diverged
    # Make sure it works as expected
    self.assertEqual(invoice.getCausalityState(), 'diverged')
    self.assertEqual(invoice_2.getSimulationState(), 'cancelled')
    self.assertEqual(len(invoice.getMovementList()), 2)
    expected_set = set([
        (resource,quantity,price),
        (resource_2, quantity_2,price_2)])
    result_set = set(sorted(
      [(x.getResource(), x.getQuantity(), x.getPrice()) for x in invoice.getMovementList()],
      key=lambda x: x[1]))
    self.assertEqual(expected_set, result_set)

  def test_subcontent_reindexing(self):
    """Tests, that modification on Order are propagated to lines and cells
    during reindxation"""
    invoice = self.portal.getDefaultModule(self.invoice_portal_type
        ).newContent(portal_type=self.invoice_portal_type,
            created_by_builder=1)
    self.tic()
    invoice_line = invoice.newContent(
        portal_type=self.invoice_line_portal_type)
    invoice_cell = invoice_line.newContent(
        portal_type=self.invoice_cell_portal_type)
    transaction_line = invoice.newContent(
        portal_type=self.invoice_transaction_line_portal_type)
    self._testSubContentReindexing(invoice, [invoice_line, transaction_line,
      invoice_cell])

  def test_AccountingTransactionModuleListboxTradeConditionColumn(self):
    """Check listbox Trade Condition column displays the trade condition
    when there are multiple documents related by specialise category.
    """
    # test init
    accounting_module = self.portal.accounting_module
    whatever_object = accounting_module.newContent(
      portal_type=self.invoice_portal_type,
    )
    trade_condition_title = "Trade Condition from %s" % self.id()
    trade_condition = self.portal.getDefaultModule(self.trade_condition_portal_type).newContent(
      portal_type=self.trade_condition_portal_type,
      title=trade_condition_title,
    )
    sale_invoice = accounting_module.newContent(
      portal_type=self.invoice_portal_type,
    )

    # actual test
    # Check listbox Sale Trade Condition column displays the trade condition
    # when there are multiple documents related by specialise category.
    accounting_listbox = accounting_module.AccountingTransactionModule_viewAccountingTransactionList.listbox
    self.assertIn(("specialise_trade_condition_title", "Trade Condition"), accounting_listbox.get_value("columns") + accounting_listbox.get_value("all_columns"))
    sale_invoice.setSpecialiseValueList([whatever_object])
    self.tic()
    sale_invoice_brain, = self.portal.portal_catalog(uid=sale_invoice.getUid(), select_list=["specialise_trade_condition_title"], limit=1)
    self.assertEqual(sale_invoice_brain.specialise_trade_condition_title, None)
    sale_invoice.setSpecialiseValueList([whatever_object, trade_condition])
    self.tic()
    sale_invoice_brain, = self.portal.portal_catalog(uid=sale_invoice.getUid(), select_list=["specialise_trade_condition_title"], limit=1)
    self.assertEqual(sale_invoice_brain.specialise_trade_condition_title, trade_condition_title)

class TestSaleInvoice(TestSaleInvoiceMixin, TestInvoice, ERP5TypeTestCase):
  """Tests for sale invoice.
  """
  quiet = 0

  @UnrestrictedMethod
  def createCategories(self):
    TestPackingListMixin.createCategories(self)
    TestInvoiceMixin.createCategories(self)

  getNeededCategoryList = TestInvoiceMixin.getNeededCategoryList

  def test_01_SimpleInvoice(self, quiet=quiet):
    """
    Checks that a Simple Invoice is created from a Packing List
    """
    if not quiet:
      self.logMessage('Simple Invoice')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepSetReadyPackingList
        stepTic
        stepStartPackingList
        stepCheckInvoicingRule
        stepTic
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckInvoiceBuilding
        stepRebuildAndCheckNothingIsCreated
        stepCheckInvoicesConsistency
        stepCheckInvoiceLineHasReferenceAndIntIndex
      """)
    sequence_list.play(self, quiet=quiet)

  def stepCreateCurrency(self, sequence):
    currency = self.portal.currency_module.newContent(
      portal_type="Currency", title="Currency",
      base_unit_quantity=0.01)
    sequence.edit(currency=currency)

  def stepCheckInvoiceWithBadPrecision(self, sequence):
    portal = self.portal
    vendor = sequence.get('vendor')
    invoice = portal.accounting_module.newContent(
      portal_type="Sale Invoice Transaction",
      specialise=self.business_process,
      source_section_value=vendor,
      start_date=self.datetime,
      price_currency_value=sequence.get('currency'),
      destination_section_value=sequence.get('client1'),
      source_value=vendor)
    resource = self.portal.getDefaultModule(
        self.resource_portal_type).newContent(
                    portal_type=self.resource_portal_type,
                    title='Resource',
                    sale_supply_line_source_account="account_module/sale",
                    product_line='apparel')
    invoice.newContent(portal_type="Invoice Line",
      resource_value=resource, quantity=1, price=0.014)
    invoice.newContent(portal_type="Invoice Line",
      resource_value=resource, quantity=1, price=0.014)
    self.tic()
    invoice.plan()
    invoice.confirm()
    self.tic()
    invoice.start()
    self.tic()
    movement_list = invoice.getMovementList(
        portal_type=invoice.getPortalAccountingMovementTypeList())
    receivable_line = [m for m in movement_list \
      if m.getSourceValue().getAccountType() == \
        "asset/receivable"][0]
    self.assertEqual(0.03, receivable_line.getSourceDebit())
    data = invoice.Invoice_getODTDataDict()
    precision = invoice.getQuantityPrecisionFromResource(
      invoice.getResource())
    self.assertEqual(round(data['total_price'], precision),
      receivable_line.getSourceDebit())
    vat_line = [m for m in movement_list \
      if m.getSourceValue().getAccountType() == \
        "liability/payable/collected_vat"][0]
    self.assertEqual(0.0, vat_line.getSourceDebit())
    income_line = [m for m in movement_list \
      if m.getSourceValue().getAccountType() == \
        "income"][0]
    self.assertEqual(0.03, income_line.getSourceCredit())

  def test_AccountingTransaction_roundDebitCredit(self):
    """
      Check that with two invoice lines with total price equal 0.14,
      the receivable line will be 0.03 and vat line 0
    """
    sequence_list = SequenceList()
    sequence_list.addSequenceString("""
      stepCreateCurrency
      stepCreateEntities
      stepCheckInvoiceWithBadPrecision
    """)
    sequence_list.play(self)

  def test_02_TwoInvoicesFromTwoPackingList(self, quiet=quiet):
    """
    This test was created for the following bug:
        - an order is created and confirmed
        - the packing list is split
        - the 2 packing list are delivered (at different date)
        - 2 invoices are built, then we set the same date on both of them
        - the accounting rules are generated and put in only one invoice !!,
          so we have an invoice with twice the number of accounting rules
          and an invoice with no accounting rules. both invoices are wrong
    """
    if not quiet: self.logMessage('Two Invoices from Two Packing List')
    sequence_list = SequenceList()
    for base_sequence in (self.TWO_PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepSetReadyPackingList
        stepSetReadyNewPackingList
        stepTic
        stepStartPackingList
        stepStartNewPackingList
        stepTic
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckTwoInvoices
        stepStartTwoInvoices
        stepTic
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckTwoInvoicesTransactionLines
        stepCheckInvoicesConsistency
      """)
    sequence_list.play(self, quiet=quiet)

  def test_03_InvoiceEditAndInvoiceRule(self, quiet=quiet):
    """
    Invoice Rule should not be applied on invoice lines created from\
    Packing List.

    We want to prevent this from happening:
      - Create a packing list
      - An invoice is created from packing list
      - Invoice is edited, updateSimulation is called
      - A new Invoice Rule is created for this invoice, and accounting
        movements for this invoice are present twice in the simulation.
    """
    if not quiet:
      self.logMessage('Invoice Edit')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepSetReadyPackingList
        stepTic
        stepStartPackingList
        stepCheckInvoicingRule
        stepTic
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckInvoiceBuilding
        stepEditInvoice
        stepTic
        stepCheckInvoiceRuleNotAppliedOnInvoiceEdit
        stepCheckInvoicesConsistency
      """)
    sequence_list.play(self, quiet=quiet)

  def test_04_PackingListEditAndInvoiceRule(self, quiet=quiet):
    """
    Delivery Rule should not be applied on packing list lines created\
    from Order.
    """
    if not quiet:
      self.logMessage('Packing List Edit')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepEditPackingList
        stepTic
        stepCheckDeliveryRuleNotAppliedOnPackingListEdit
      """)
    sequence_list.play(self, quiet=quiet)

  def test_05_InvoiceEditPackingListLine(self, quiet=quiet):
    """
    Checks that editing a Packing List Line still creates a correct
    Invoice
    """
    if not quiet:
      self.logMessage('Packing List Line Edit')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
    """
      stepEditPackingListLine
      stepTic
      stepCheckPackingListIsDiverged
      stepAssertCausalityStateIsNotSolvedInConsistencyMessage
      stepSetReadyWorkflowTransitionIsBlockByConsistency
      stepAcceptDecisionDescriptionPackingList
      stepTic
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepCheckInvoicingRule
      stepTic
      stepInvoiceBuilderAlarm
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
      stepCheckInvoicesConsistency
    """)
    sequence_list.play(self, quiet=quiet)

  def test_06_InvoiceDeletePackingListLine(self, quiet=quiet):
    """
    Checks that deleting a Packing List Line still creates a correct
    Invoice
    """
    if not quiet:
      self.logMessage('Packing List Line Delete')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_TWO_LINES_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
    """
      stepDeletePackingListLine
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepCheckInvoicingRule
      stepTic
      stepInvoiceBuilderAlarm
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
      stepCheckInvoicesConsistency
      stepTic
    """)
    sequence_list.play(self, quiet=quiet)

  def test_07_InvoiceAddPackingListLine(self, quiet=quiet):
    """
    Checks that adding a Packing List Line still creates a correct
    Invoice
    """
    if not quiet:
      self.logMessage('Packing List Line Add')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE,
        self.PACKING_LIST_TWO_LINES_DEFAULT_SEQUENCE) :
      sequence_list.addSequenceString(
        base_sequence +
    """
      stepAddPackingListLine
      stepTic
      stepSetContainerFullQuantity
      stepTic
      stepSetReadyPackingList
      stepTic
      stepStartPackingList
      stepCheckInvoicingRule
      stepTic
      stepInvoiceBuilderAlarm
      stepTic
      stepCheckInvoiceBuilding
      stepRebuildAndCheckNothingIsCreated
      stepCheckInvoicesConsistency
    """)
    sequence_list.play(self, quiet=quiet)

  def test_08_InvoiceDecreaseQuantity(self, quiet=quiet):
    """
    Change the quantity of a Invoice Line,
    check that the invoice is divergent,
    then split and defer, and check everything is solved
    """
    if not quiet:
      self.logMessage('Invoice Decrease Quantity')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding

    stepDecreaseInvoiceLineQuantity
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepSplitAndDeferInvoice
    stepTic
    stepInvoiceBuilderAlarm
    stepTic

    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved
    stepCheckInvoiceSplitted

    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """
    self.playSequence(sequence, quiet=quiet)

  @newSimulationExpectedFailure
  def test_09_InvoiceChangeStartDateFail(self, quiet=quiet):
    """
    Change the start_date of a Invoice Line,
    check that the invoice is divergent,
    then accept decision, and check Packing list is *not* divergent,
    because Unify Solver does not propagage the change to the upper
    simulation movement.
    """
    if not quiet:
      self.logMessage('Invoice Change Start Date')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding

    stepChangeInvoiceStartDate
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepUnifyStartDateWithDecisionInvoice
    stepTic

    stepCheckInvoiceNotSplitted
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """
    self.playSequence(sequence, quiet=quiet)

  @newSimulationExpectedFailure
  def test_09b_InvoiceChangeStartDateSucceed(self, quiet=quiet):
    """
    Change the start_date of a Invoice Line,
    check that the invoice is divergent,
    deliver the Packing List to make sure it's frozen,
    then accept decision, and check everything is solved
    """
    if not quiet:
      self.logMessage('Invoice Change Sart Date')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic

    stepChangeInvoiceStartDate
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepUnifyStartDateWithDecisionInvoice
    stepTic

    stepCheckInvoiceNotSplitted
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """
    self.playSequence(sequence, quiet=quiet)

  def test_10_AcceptDecisionOnPackingList(self, quiet=quiet):
    """
    - Increase or Decrease the quantity of a Packing List line
    - Accept Decision on Packing List
    - Packing List must not be divergent and use new quantity
    - Invoice must not be divergent and use new quantity
    """
    if not quiet:
      self.logMessage('InvoiceAcceptDecisionOnPackingList')
    end_sequence = \
    """
    stepSetContainerFullQuantity
    stepCheckPackingListIsCalculating
    stepTic
    stepCheckPackingListIsDiverged
    stepAcceptDecisionQuantity
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted

    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding

    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepStartInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceNotSplitted
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """

    mid_sequence_list = ["""
    stepCheckInvoicingRule
    stepDecreasePackingListLineQuantity
    """, """
    stepCheckInvoicingRule
    stepIncreasePackingListLineQuantity
    """]

    sequence_list = SequenceList()
    for seq in mid_sequence_list:
      sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
          seq + end_sequence
      sequence_list.addSequenceString(sequence)
    sequence_list.play(self, quiet=quiet)

  def test_16a_ManuallyAddedMovementsManyTransactions(self, quiet=quiet):
    """
    Checks that adding invoice lines and accounting lines to one invoice
    generates correct simulation

    In this case checks what is happening, where movements are added in
    one transaction and edited in another
    """
    if not quiet:
      self.logMessage('Invoice with Manually Added Movements in separate transactions')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
          base_sequence +
          """
          stepSetReadyPackingList
          stepTic
          stepStartPackingList
          stepCheckInvoicingRule
          stepTic
          stepInvoiceBuilderAlarm
          stepTic
          stepCheckInvoiceBuilding
          stepRebuildAndCheckNothingIsCreated
          stepCheckInvoicesConsistency
          stepAddInvoiceLinesManyTransactions
          stepTic
          stepCheckInvoiceIsSolved
          stepStartInvoice
          stepTic
          stepCheckSimulationTrees
          """)
    sequence_list.play(self, quiet=quiet)


  def test_11_AcceptDecisionOnPackingListAndInvoice(self, quiet=quiet):
    """
    - Increase or Decrease the quantity of a Packing List line
    - Accept Decision on Packing List
    - Packing List must not be divergent and use new quantity
    - Put old quantity on Invoice
    - Accept Decision on Invoice
    - Packing List must not be divergent and use new quantity
    - Invoice must not be divergent and use old quantity
    """
    if not quiet:
      self.logMessage('InvoiceAcceptDecisionOnPackingListAndInvoice')
    mid_sequence = \
    """
    stepSetContainerFullQuantity
    stepCheckPackingListIsCalculating
    stepTic
    stepCheckPackingListIsDiverged
    stepAcceptDecisionQuantity
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted

    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding

    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule
    """
    end_sequence = \
    """
    stepCheckInvoiceIsDiverged
    stepAcceptDecisionQuantityInvoice
    stepTic
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved
    stepStartInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule
    stepCheckInvoiceNotSplitted
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """

    mid_sequence_list = [("""
    stepCheckInvoicingRule
    stepDecreasePackingListLineQuantity
    """, """
    stepIncreaseInvoiceLineQuantity
    stepTic
    """), ("""
    stepCheckInvoicingRule
    stepIncreasePackingListLineQuantity
    """, """
    stepDecreaseInvoiceLineQuantity
    stepTic
    """)]

    sequence_list = SequenceList()
    for seq1, seq2 in mid_sequence_list:
      sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
          seq1 + mid_sequence + seq2 + end_sequence
      sequence_list.addSequenceString(sequence)
    sequence_list.play(self, quiet=quiet)

  def test_12_SplitPackingListAndAcceptInvoice(self, quiet=quiet):
    """
    - Decrease the quantity of a Packing List line
    - Split and Defer on Packing List
    - Packing List must not be divergent and use new quantity
    - splitted Packing List must not be divergent and use old - new quantity

    - Put old quantity on Invoice1
    - Accept Decision on Invoice1
    - Packing List must not be divergent and use new quantity
    - splitted Packing List must not be divergent and use old - new quantity
    - Invoice1 must not be divergent and use old quantity

    - set Invoice2 quantity to 0
    - Accept Decision on Invoice2
    - Packing List must not be divergent and use new quantity
    - splitted Packing List must not be divergent and use old - new quantity
    - Invoice1 must not be divergent and use old quantity
    - Invoice2 must not be divergent and use 0 as quantity
    """
    if not quiet:
      self.logMessage('InvoiceSplitPackingListAndAcceptInvoice')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepCheckInvoicingRule
    stepDecreasePackingListLineQuantity
    stepSetContainerFullQuantity
    stepCheckPackingListIsCalculating
    stepTic
    stepCheckPackingListIsDiverged
    stepSplitAndDeferPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListSplitted

    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListSplitted

    stepIncreaseInvoiceLineQuantity
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepAcceptDecisionQuantityInvoice
    stepTic
    stepStartInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceIsSolved
    stepCheckInvoiceNotSplitted
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency

    stepSwitchPackingLists

    stepAddPackingListContainer
    stepSetContainerFullQuantity
    stepTic
    stepCheckPackingListIsSolved
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsSolved

    stepSetInvoiceLineQuantityToZero
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepAcceptDecisionQuantityInvoice
    stepTic
    stepStartInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceIsSolved
    stepCheckInvoiceNotSplitted
    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """
    self.playSequence(sequence, quiet=quiet)

  def test_13_SplitAndDeferInvoice(self, quiet=quiet):
    """
    - Accept Order, Accept Packing List
    - Decrease quantity on Invoice
    - Split and defer Invoice
    - Accept Invoice
    - Accept splitted Invoice
    - Packing List must not be divergent and use old quantity
    - Invoice must not be divergent and use new quantity
    - splitted Invoice must not be divergent and use old - new quantity
    """
    if not quiet:
      self.logMessage('InvoiceSplitAndDeferInvoice')
    sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted

    stepDecreaseInvoiceLineQuantity
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepSplitAndDeferInvoice
    stepTic
    stepStartInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved
    stepCheckInvoiceSplitted

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency

    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepSwitchInvoices

    stepStartInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """
    self.playSequence(sequence, quiet=quiet)

  def test_14_AcceptDecisionOnInvoice(self, quiet=quiet):
    """
    - Accept Order, Accept Packing List
    - Increase or Decrease quantity on Invoice
    - Accept Decision on Invoice
    - Accept Invoice
    - Packing List must not be divergent and use old quantity
    - Invoice must not be divergent and use new quantity
    """
    if not quiet:
      self.logMessage('InvoiceAcceptDecisionOnInvoice')
    mid_sequence = \
    """
    stepSetReadyPackingList
    stepTic
    stepStartPackingList
    stepCheckInvoicingRule
    stepCheckInvoiceTransactionRule
    stepTic
    stepInvoiceBuilderAlarm
    stepTic
    stepCheckInvoiceBuilding
    stepStopPackingList
    stepTic
    stepDeliverPackingList
    stepTic
    stepCheckPackingListIsSolved
    stepCheckPackingListNotSplitted
    """
    end_sequence = \
    """
    stepCheckInvoiceIsDivergent
    stepCheckInvoiceIsCalculating
    stepTic
    stepCheckInvoiceIsDiverged
    stepAcceptDecisionQuantityInvoice
    stepTic
    stepStartInvoice
    stepTic
    stepStopInvoice
    stepTic
    stepDeliverInvoice
    stepTic

    stepCheckPackingListIsNotDivergent
    stepCheckPackingListIsSolved
    stepCheckInvoiceTransactionRule

    stepCheckInvoiceNotSplitted
    stepCheckInvoiceIsNotDivergent
    stepCheckInvoiceIsSolved

    stepRebuildAndCheckNothingIsCreated
    stepCheckInvoicesConsistency
    """

    mid_sequence_list = ["""
    stepDecreaseInvoiceLineQuantity
    """, """
    stepIncreaseInvoiceLineQuantity
    """]

    sequence_list = SequenceList()
    for seq in mid_sequence_list:
      sequence = self.PACKING_LIST_DEFAULT_SEQUENCE + \
          mid_sequence + seq + end_sequence
      sequence_list.addSequenceString(sequence)
    sequence_list.play(self, quiet=quiet)


  def test_Reference(self):
    # A reference is set automatically on Sale Invoice Transaction
    supplier = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Supplier')
    client = self.portal.organisation_module.newContent(
                            portal_type='Organisation',
                            title='Client')
    currency = self.portal.currency_module.newContent(
                            portal_type='Currency')
    invoice = self.portal.accounting_module.newContent(
                    portal_type='Sale Invoice Transaction',
                    start_date=DateTime(),
                    price_currency_value=currency,
                    resource_value=currency,
                    source_section_value=supplier,
                    destination_section_value=client)
    self.portal.portal_workflow.doActionFor(invoice, 'confirm_action')

    self.assertEqual('1', invoice.getReference())

  def test_16_ManuallyAddedMovements(self, quiet=quiet):
    """
    Checks that adding invoice lines and accounting lines to one invoice
    generates correct simulation
    """
    if not quiet:
      self.logMessage('Invoice with Manually Added Movements')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
          base_sequence +
          """
          stepSetReadyPackingList
          stepTic
          stepStartPackingList
          stepCheckInvoicingRule
          stepTic
          stepInvoiceBuilderAlarm
          stepTic
          stepCheckInvoiceBuilding
          stepRebuildAndCheckNothingIsCreated
          stepCheckInvoicesConsistency
          stepAddInvoiceLines
          stepTic
          stepStartInvoice
          stepTic
          stepCheckSimulationTrees
          """)
    sequence_list.play(self, quiet=quiet)

  def test_17_ManuallyAddedWrongMovements(self, quiet=quiet):
    """
    Checks that adding invoice lines and accounting lines to one invoice
    generates correct simulation, even when adding very wrong movements
    """
    if not quiet:
      self.logMessage('Invoice with Manually Added Movements')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
          base_sequence +
          """
          stepSetReadyPackingList
          stepTic
          stepStartPackingList
          stepCheckInvoicingRule
          stepTic
          stepInvoiceBuilderAlarm
          stepTic
          stepCheckInvoiceBuilding
          stepAddWrongInvoiceLines
          stepTic
          stepStartInvoice
          stepCheckStartInvoiceFail
          stepCheckSimulationTrees
          """)
    sequence_list.play(self, quiet=quiet)

  def test_18_compareInvoiceAndPackingList(self, quiet=quiet):
    """
    Checks that a Simple Invoice is created from a Packing List
    """
    if not quiet:
      self.logMessage('Simple Invoice')
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepSetReadyPackingList
        stepTic
        stepStartPackingList
        stepCheckInvoicingRule
        stepTic
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckInvoiceBuilding
        stepCheckInvoicesConsistency
        stepCheckPackingListInvoice
      """)
    sequence_list.play(self, quiet=quiet)

  def _adoptDivergenceOnPackingList(self, packing_list, divergence_list):
    builder_list = packing_list.getBuilderList()
    for builder in builder_list:
      builder.solveDivergence(packing_list.getRelativeUrl(),
                              divergence_to_adopt_list=divergence_list)

  def test_accept_quantity_divergence_on_invoice_with_started_packing_list(
                        self, quiet=quiet):
    # only applies to sale invoice, because purchase invoices are not built yet
    # when the packing list is in started state
    sequence_list = SequenceList()
    sequence = sequence_list.addSequenceString(self.PACKING_LIST_DEFAULT_SEQUENCE)
    sequence_list.play(self, quiet=quiet)

    packing_list = sequence.get('packing_list')
    packing_list.setReady()
    packing_list.start()
    self.assertEqual('started', packing_list.getSimulationState())
    self.tic()
    self.stepInvoiceBuilderAlarm()
    self.tic()

    invoice = packing_list.getCausalityRelatedValue(
                                  portal_type=self.invoice_portal_type)
    self.assertNotEqual(invoice, None)
    invoice_line_list = invoice.getMovementList()
    self.assertEqual(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]

    new_quantity = invoice_line.getQuantity() * 2
    invoice_line.setQuantity(new_quantity)

    self.tic()

    self.assertTrue(invoice.isDivergent())
    divergence_list = invoice.getDivergenceList()
    self.assertEqual(1, len(divergence_list))

    divergence = divergence_list[0]
    self.assertEqual('quantity', divergence.tested_property)

    # accept decision
    self._acceptDivergenceOnInvoice(invoice, divergence_list)

    self.tic()
    self.assertEqual('solved', invoice.getCausalityState())

    self.assertEqual([], invoice.getDivergenceList())
    self.assertEqual(new_quantity, invoice_line.getQuantity())
    self.assertEqual(new_quantity,
          invoice_line.getDeliveryRelatedValue(portal_type='Simulation Movement'
              ).getQuantity())

    if invoice_line.getDeliveryRelatedValue().getParentValue().getSpecialiseId() == \
        'new_invoice_simulation_rule':
      # With new simulation solvers, changes on simulation movements will
      # not backtrack.
      pass
    else:
      # With legacy simulation solvers, changes on simulation movements
      # will backtrack if simulation movements are not frozen.
      # the packing list is divergent, because it is not frozen
      self.assertEqual('diverged', packing_list.getCausalityState())
      divergence_list = packing_list.getDivergenceList()
      self.assertEqual(1, len(divergence_list))
      divergence = divergence_list[0]
      self.assertEqual('quantity', divergence.tested_property)
      # if we adopt prevision on this packing list, both invoice and
      # packing list will be solved
      self._adoptDivergenceOnPackingList(packing_list, divergence_list)
      self.tic()
    self.assertEqual('solved', packing_list.getCausalityState())
    self.assertEqual('solved', invoice.getCausalityState())

  def test_19_SimpleInvoiceModifyArrow(self):
    """
    Check we can modify arrow on an invoice without having building issues
    of transaction lines
    """
    sequence_list = SequenceList()
    for base_sequence in (self.PACKING_LIST_DEFAULT_SEQUENCE, ) :
      sequence_list.addSequenceString(
        base_sequence +
      """
        stepSetReadyPackingList
        stepTic
        stepStartPackingList
        stepCheckInvoicingRule
        stepTic
        stepInvoiceBuilderAlarm
        stepTic
        stepCheckInvoiceBuilding
      """)
    sequence_list.play(self)
    sequence = sequence_list.getSequenceList()[0]
    invoice = sequence.get("invoice")
    self.assertEqual("confirmed", invoice.getSimulationState())
    self.assertEqual("solved", invoice.getCausalityState())
    self.portal.portal_workflow.doActionFor(invoice, "start_action")
    other_client = sequence.get("organisation3")
    invoice.setDestinationSectionValue(other_client)
    self.tic()
    self.assertEqual("diverged", invoice.getCausalityState())
    self.assertEqual(set([("411", -65714.22),
                         ("44571", 10769.22),
                         ("70712", 54945.00)]),
                     set([(x.getSourceValue().getGapId(),
                           x.getQuantity()) for x in \
                           invoice.objectValues(
                    portal_type="Sale Invoice Transaction Line")]))

class TestPurchaseInvoice(TestInvoice, ERP5TypeTestCase):
  """Tests for purchase invoice.
  """
  resource_portal_type = 'Product'
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  order_cell_portal_type = 'Purchase Order Cell'
  packing_list_portal_type = 'Purchase Packing List'
  packing_list_line_portal_type = 'Purchase Packing List Line'
  packing_list_cell_portal_type = 'Purchase Packing List Cell'
  invoice_portal_type = 'Purchase Invoice Transaction'
  invoice_transaction_line_portal_type = 'Purchase Invoice Transaction Line'
  invoice_line_portal_type = 'Invoice Line'
  invoice_cell_portal_type = 'Invoice Cell'
  trade_condition_portal_type = 'Purchase Trade Condition'

  # default sequence for one line of not varianted resource.
  PACKING_LIST_DEFAULT_SEQUENCE = """
      stepCreateEntities
      stepCreateCurrency
      stepCreateOrder
      stepSetOrderProfile
      stepSetOrderPriceCurrency
      stepCreateNotVariatedResource
      stepTic
      stepCreateOrderLine
      stepSetOrderLineResource
      stepSetOrderLineDefaultValues
      stepOrderOrder
      stepTic
      stepCheckDeliveryBuilding
      stepConfirmOrder
      stepTic
      stepPackingListBuilderAlarm
      stepTic
      stepCheckOrderRule
      stepCheckOrderSimulation
      stepCheckDeliveryBuilding
      stepTic
    """

class OpenDocumentTextFile :
  def __init__ (self, filelikeobj):
    with zipfile.ZipFile(filelikeobj) as z:
      self.content = xml.dom.minidom.parseString(z.read("content.xml"))

  def toString (self) :
    """ Converts the document to a string. """
    buffer_ = u""
    for val in ["text:p", "text:h", "text:list"]:
      for paragraph in self.content.getElementsByTagName(val) :
        buffer_ += self.textToString(paragraph) + "\n"
    return buffer_

  def textToString(self, element) :
    buffer_ = u""
    for node in element.childNodes :
      if node.nodeType == xml.dom.Node.TEXT_NODE :
        buffer_ += node.nodeValue
      elif node.nodeType == xml.dom.Node.ELEMENT_NODE :
        buffer_ += self.textToString(node)
    return buffer_

import unittest
def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSaleInvoice))
  suite.addTest(unittest.makeSuite(TestPurchaseInvoice))
  return suite
