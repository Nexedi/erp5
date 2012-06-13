import unittest
from DateTime import DateTime
from testLegacyTradeCondition import TestWithSaleOrder, \
    TestWithPurchaseOrder, TestWithSaleInvoice, TestWithPurchaseInvoice, \
    TradeConditionTestCase, AccountingBuildTestCase

class TestTaxLineCalculation(TradeConditionTestCase):
  """Test calculating Tax Lines.
  """
  def test_apply_trade_condition_twice_and_tax_lines(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
    
    # if we apply twice, we don't have the tax lines twice
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))

  def test_apply_trade_condition_after_line_creation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    self.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

  def test_simple_tax_model_line_calculation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)

    self.commit()
    # at the end of transaction, tax lines are updated
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(20, tax_line.getTotalPrice())
    
  def test_tax_model_line_calculation_with_two_lines(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line_1 = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=3,
                          price=10,)
    order_line_2 = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=7,
                          price=10,)
    
    self.commit()
    # at the end of transaction, tax lines are updated
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(20, tax_line.getTotalPrice())
    
    order_line_1_tax_line_list = \
      order_line_1.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(1, len(order_line_1_tax_line_list))
    tax_line = order_line_1_tax_line_list[0]
    self.assertEquals(30, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(6, tax_line.getTotalPrice())

    order_line_2_tax_line_list = \
      order_line_2.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(1, len(order_line_2_tax_line_list))
    tax_line = order_line_2_tax_line_list[0]
    self.assertEquals(70, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(14, tax_line.getTotalPrice())

  def test_tax_on_tax(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    base_2 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 2')
    tax2 = self.portal.tax_module.newContent(
                          portal_type='Tax',
                          title='Tax 2')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  base_contribution_value=base_2,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_2,
                  float_index=2,
                  efficiency=0.5,
                  resource_value=tax2)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    self.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(2, len(tax_line_list))
    tax_line1 = [tl for tl in tax_line_list if
                   tl.getResourceValue() == self.tax][0]
    self.assertEquals(0, tax_line1.getQuantity())
    self.assertEquals(0.2, tax_line1.getPrice())
    self.assertEquals(1, tax_line1.getFloatIndex())
    self.assertEquals([base_1], tax_line1.getBaseApplicationValueList())
    self.assertEquals([base_2], tax_line1.getBaseContributionValueList())

    tax_line2 = [tl for tl in tax_line_list if
                   tl.getResourceValue() == tax2][0]
    self.assertEquals(0, tax_line2.getQuantity())
    self.assertEquals(0.5, tax_line2.getPrice())
    self.assertEquals(2, tax_line2.getFloatIndex())
    self.assertEquals([base_2], tax_line2.getBaseApplicationValueList())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=3,
                          price=10,)
    self.commit()
    self.assertEquals(30, tax_line1.getQuantity())
    self.assertEquals((30*0.2), tax_line2.getQuantity())
    
    order_line.setQuantity(5)
    self.commit()
    self.assertEquals(50, tax_line1.getQuantity())
    self.assertEquals((50*0.2), tax_line2.getQuantity())
    
    tax_movement_list = order_line.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(2, len(tax_movement_list))
    tax_1_movement = [m for m in tax_movement_list if m.getPrice() == 0.2][0]
    self.assertEquals(tax_1_movement.getQuantity(), 50)
    tax_2_movement = [m for m in tax_movement_list if m.getPrice() == 0.5][0]
    self.assertEquals(tax_2_movement.getQuantity(), 50*0.2)


  def test_update_order_line_quantity_update_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)

    self.commit()
    # tax lines are updated
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(20, tax_line.getTotalPrice())
    
    # change the quantity on order_line,
    order_line.setQuantity(20)
    self.commit()
    # the tax line is updated (by an interraction workflow at the end of
    # transaction)
    self.assertEquals(200, tax_line.getQuantity())
    self.assertEquals(40, tax_line.getTotalPrice())

  def test_delete_order_line_quantity_update_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)

    self.commit()
    # tax lines are updated
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(20, tax_line.getTotalPrice())
    
    # delete the order line
    self.order.manage_delObjects([order_line.getId()])
    # the tax line is updated
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(0, tax_line.getTotalPrice())

  def test_clone_order_line_quantity_update_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)

    self.commit()
    # tax lines are updated
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(20, tax_line.getTotalPrice())
    
    # clone the order line
    cloned_order_line = order_line.Base_createCloneDocument(batch_mode=1)
    # the tax line is updated
    self.assertEquals(200, tax_line.getQuantity())
    self.assertEquals(40, tax_line.getTotalPrice())

  def test_order_cell_and_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    # make a resource with size variation
    self.resource.setVariationBaseCategoryList(('size',))
    self.resource.setVariationCategoryList(('size/big', 'size/small'))

    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,)
    order_line.setVariationCategoryList(('size/big', 'size/small'))
    order_line.updateCellRange(base_id='movement')
    cell_red = order_line.newCell('size/big',
                                  portal_type=self.order_cell_type,
                                  base_id='movement')
    cell_red.setMappedValuePropertyList(['quantity', 'price'])
    cell_red.setPrice(5)
    cell_red.setQuantity(10)
    cell_blue = order_line.newCell('size/small',
                             portal_type=self.order_cell_type,
                             base_id='movement')
    cell_blue.setMappedValuePropertyList(['quantity', 'price'])
    cell_blue.setPrice(2)
    cell_blue.setQuantity(25)
    self.assertEquals(100, order_line.getTotalPrice(fast=0))
    
    self.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
    
    self.assertEquals(100, self.order.getTotalPrice(fast=0))
    self.assertEquals(120, self.order.getTotalNetPrice(fast=0))


  def test_hierarchical_order_line_and_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)

    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,)
    suborder_line1 = order_line.newContent(
                          portal_type=self.order_line_type,
                          quantity=4,
                          price=5)
    suborder_line2 = order_line.newContent(
                          portal_type=self.order_line_type,
                          quantity=2,
                          price=40)

    self.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
  
  def test_base_contribution_pseudo_acquisition(self):
    base_1 = self.base_amount.newContent(portal_type='Category',
                                         title='Base 1')
    self.resource.setBaseContributionValueList((base_1,))
    line = self.order.newContent(portal_type=self.order_line_type)
    self.assertEquals([], line.getBaseContributionValueList())
    line.setResourceValue(self.resource)
    self.assertEquals([base_1], line.getBaseContributionValueList())
    line.setBaseContributionValueList([])
    self.assertEquals([], line.getBaseContributionValueList())

  def test_multiple_order_line_multiple_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    base_2 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 2')
    self.resource.setBaseContributionValueList((base_1, base_2))
    tax_model_line_1 = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.1,
                  resource_value=self.tax)
    tax_model_line_2 = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_2,
                  float_index=2,
                  efficiency=0.2,
                  resource_value=self.tax)
    tax_model_line_1_2 = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value_list=(base_1, base_2),
                  float_index=3,
                  efficiency=0.3,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    line_1 = self.order.newContent(
                  portal_type=self.order_line_type,
                  quantity=1, price=1,
                  resource_value=self.resource,
                  base_contribution_value_list=(base_1,))
    # -> tax_model_line_1 and tax_model_line_1_2 are applicable
    line_2 = self.order.newContent(
                  portal_type=self.order_line_type,
                  quantity=2, price=2,
                  resource_value=self.resource,
                  base_contribution_value_list=(base_2,))
    # -> tax_model_line_2 and tax_model_line_1_2 are applicable
    line_3 = self.order.newContent(
                  portal_type=self.order_line_type,
                  quantity=3, price=3,
                  resource_value=self.resource,
                  base_contribution_value_list=(base_1, base_2))
    # -> tax_model_line_1, tax_model_line_2 and tax_model_line_1_2 are applicable
    #  (but they are not applied twice)

    self.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(3, len(tax_line_list))
    tax_line_1 = [x for x in tax_line_list if x.getPrice() == 0.1][0]
    tax_line_2 = [x for x in tax_line_list if x.getPrice() == 0.2][0]
    tax_line_3 = [x for x in tax_line_list if x.getPrice() == 0.3][0]

    self.assertEquals(sum([line_1.getTotalPrice(),
                           line_3.getTotalPrice()]), tax_line_1.getQuantity())
    self.assertEquals(sum([line_2.getTotalPrice(),
                           line_3.getTotalPrice()]), tax_line_2.getQuantity())
    self.assertEquals(sum([line_1.getTotalPrice(),
                           line_2.getTotalPrice(),
                           line_3.getTotalPrice()]), tax_line_3.getQuantity())

    tax_movement_list = line_1.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(2, len(tax_movement_list))
    tax_1_movement = [m for m in tax_movement_list if m.getPrice() == 0.1][0]
    self.assertEquals(tax_1_movement.getQuantity(), 1)
    tax_3_movement = [m for m in tax_movement_list if m.getPrice() == 0.3][0]
    self.assertEquals(tax_3_movement.getQuantity(), 1)
    
    tax_movement_list = line_2.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(2, len(tax_movement_list))
    tax_2_movement = [m for m in tax_movement_list if m.getPrice() == 0.2][0]
    self.assertEquals(tax_2_movement.getQuantity(), 4)
    tax_3_movement = [m for m in tax_movement_list if m.getPrice() == 0.3][0]
    self.assertEquals(tax_3_movement.getQuantity(), 4)
    
    tax_movement_list = line_3.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(3, len(tax_movement_list))
    tax_1_movement = [m for m in tax_movement_list if m.getPrice() == 0.1][0]
    self.assertEquals(tax_1_movement.getQuantity(), 9)
    tax_2_movement = [m for m in tax_movement_list if m.getPrice() == 0.2][0]
    self.assertEquals(tax_2_movement.getQuantity(), 9)
    tax_3_movement = [m for m in tax_movement_list if m.getPrice() == 0.3][0]
    self.assertEquals(tax_3_movement.getQuantity(), 9)
    
  def test_temp_order(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)

    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)

    order = self.portal.getDefaultModule(self.order_type).newContent(
                          portal_type=self.order_type,
                          temp_object=1)
    order.Order_applyTradeCondition(self.trade_condition, force=1)

    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=40)
    self.commit()

    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(400, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
  
  def test_temp_order_hierarchical(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)

    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)

    order = self.portal.getDefaultModule(self.order_type).newContent(
                          portal_type=self.order_type,
                          temp_object=1)
    order.Order_applyTradeCondition(self.trade_condition, force=1)

    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,)
    suborder_line1 = order_line.newContent(
                          portal_type=self.order_line_type,
                          quantity=4,
                          price=5)
    suborder_line2 = order_line.newContent(
                          portal_type=self.order_line_type,
                          quantity=2,
                          price=40)

    self.commit()
    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
  

class TestTaxLineOrderSimulation(AccountingBuildTestCase):
  """Test Simulation of Tax Lines on Orders
  """
  def test_tax_line_simulation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    self.tic()
    related_applied_rule_list = order.getCausalityRelatedValueList(
                                      portal_type='Applied Rule')
    self.assertEquals(1, len(related_applied_rule_list))
    root_applied_rule = related_applied_rule_list[0]
    simulation_movement_list = root_applied_rule.contentValues(
                                   portal_type='Simulation Movement')
    self.assertEquals(1, len(simulation_movement_list))
    level2_applied_rule_list = simulation_movement_list[0].contentValues()
    self.assertEquals(2, len(level2_applied_rule_list))
    # first test the invoice movement, they should have base_contribution set
    # correctly
    invoice_rule_list = [ar for ar in level2_applied_rule_list if
             ar.getSpecialiseValue().getPortalType() == 'Invoicing Rule']
    self.assertEquals(1, len(invoice_rule_list))
    invoice_simulation_movement_list = invoice_rule_list[0].contentValues()
    self.assertEquals(1, len(invoice_simulation_movement_list))
    invoice_simulation_movement = invoice_simulation_movement_list[0]
    self.assertEquals(self.resource,
        invoice_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
        invoice_simulation_movement.getBaseContributionValueList())

    # now test the tax movement
    applied_tax_rule_list = [ar for ar in level2_applied_rule_list if
             ar.getSpecialiseValue().getPortalType() == 'Tax Rule']
    self.assertEquals(1, len(applied_tax_rule_list))
    tax_simulation_movement_list = applied_tax_rule_list[0].contentValues()
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]

    self.assertEquals(self.tax, tax_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
                      tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(100, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())
    
    # reexpand and check nothing changed
    root_applied_rule.expand()
    applied_tax_rule_list = [ar for ar in level2_applied_rule_list if
             ar.getSpecialiseValue().getPortalType() == 'Tax Rule']
    self.assertEquals(1, len(applied_tax_rule_list))
    tax_simulation_movement_list = applied_tax_rule_list[0].contentValues()
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]

    self.assertEquals(self.tax, tax_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
                      tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(100, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())

  def test_2_tax_lines_simulation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line1 = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order_line2 = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=7,
                          price=10,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    self.tic()
    related_applied_rule_list = order.getCausalityRelatedValueList(
                                      portal_type='Applied Rule')
    self.assertEquals(1, len(related_applied_rule_list))
    root_applied_rule = related_applied_rule_list[0]
    simulation_movement_list = root_applied_rule.contentValues(
                                   portal_type='Simulation Movement')
    self.assertEquals(2, len(simulation_movement_list))
    # line 1
    line1_simulation_movement_list = [sm for sm in simulation_movement_list
          if sm.getOrderValue() == order_line1]
    self.assertEquals(1, len(line1_simulation_movement_list))
    simulation_movement = line1_simulation_movement_list[0]
    self.assertEquals(2.0, simulation_movement.getQuantity())
    applied_tax_rule_list = [ar for ar in simulation_movement.objectValues()
        if ar.getSpecialiseValue().getPortalType() == 'Tax Rule']
    self.assertEquals(1, len(applied_tax_rule_list))
    tax_simulation_movement_list = applied_tax_rule_list[0].contentValues()
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]
    self.assertEquals(self.tax, tax_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
                      tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(30, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())
    
    # line 2
    line2_simulation_movement_list = [sm for sm in simulation_movement_list
          if sm.getOrderValue() == order_line2]
    self.assertEquals(1, len(line2_simulation_movement_list))
    simulation_movement = line2_simulation_movement_list[0]
    self.assertEquals(7., simulation_movement.getQuantity())
    applied_tax_rule_list = [ar for ar in simulation_movement.objectValues()
        if ar.getSpecialiseValue().getPortalType() == 'Tax Rule']
    self.assertEquals(1, len(applied_tax_rule_list))
    tax_simulation_movement_list = applied_tax_rule_list[0].contentValues()
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]
    self.assertEquals(self.tax, tax_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
                      tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(70, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())


  def test_tax_line_build(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setPriceCurrencyValue(self.currency)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    self.tic()
    related_delivery = order.getCausalityRelatedValue(
                  portal_type=('Purchase Packing List', 'Sale Packing List'))
    self.assertNotEquals(related_delivery, None)
    related_delivery.setReady()
    related_delivery.start()
    related_delivery.stop()
    related_delivery.deliver()
    self.assertEquals('delivered', related_delivery.getSimulationState())
    self.tic()
    
    related_invoice = related_delivery.getCausalityRelatedValue(
                  portal_type=('Purchase Invoice Transaction',
                               'Sale Invoice Transaction'))
    self.assertNotEquals(related_invoice, None)
    invoice_line_list = related_invoice.contentValues(
                  portal_type='Invoice Line')
    tax_line_list = related_invoice.contentValues(
                  portal_type='Tax Line')

    self.assertEquals(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]
    self.assertEquals(2, invoice_line.getQuantity())
    self.assertEquals(15, invoice_line.getPrice())
    self.assertEquals(self.resource, invoice_line.getResourceValue())
    self.assertEquals([base_1], invoice_line.getBaseContributionValueList())

    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(30, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals([base_1], tax_line.getBaseApplicationValueList())
    self.assertEquals([], tax_line.getBaseContributionValueList())

    self.assertEquals('solved', related_invoice.getCausalityState())

    # Of course, this invoice does not generate simulation again. New
    # applied rule is not created.
    related_applied_rule = related_invoice.getCausalityRelatedValue(
                                portal_type='Applied Rule')
    self.assertEquals(None, related_applied_rule)
    
  def test_tax_line_build_accounting(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setPriceCurrencyValue(self.currency)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    self.tic()
    related_delivery = order.getCausalityRelatedValue(
                  portal_type=('Purchase Packing List', 'Sale Packing List'))
    self.assertNotEquals(related_delivery, None)
    related_delivery.setReady()
    related_delivery.start()
    related_delivery.stop()
    related_delivery.deliver()
    self.assertEquals('delivered', related_delivery.getSimulationState())
    self.tic()
    
    related_invoice = related_delivery.getCausalityRelatedValue(
                  portal_type=('Purchase Invoice Transaction',
                               'Sale Invoice Transaction'))
    self.assertNotEquals(related_invoice, None)
    self.assertEquals('confirmed', related_invoice.getSimulationState())
    self.assertEquals('solved', related_invoice.getCausalityState())
    accounting_line_list = related_invoice.getMovementList(
                    portal_type=self.portal.getPortalAccountingMovementTypeList())
    self.assertEquals(0, len(accounting_line_list))

    related_invoice.start()
    self.tic()
    self.assertEquals('started', related_invoice.getSimulationState())
    self.assertEquals('solved', related_invoice.getCausalityState())

    accounting_line_list = related_invoice.getMovementList(
                    portal_type=self.portal.getPortalAccountingMovementTypeList())
    self.assertEquals(3, len(accounting_line_list))
    receivable_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.receivable_account][0]
    self.assertEquals(self.payable_account,
                      receivable_line.getDestinationValue())
    self.assertEquals(36, receivable_line.getSourceDebit())
    
    tax_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.collected_tax_account][0]
    self.assertEquals(self.refundable_tax_account,
                      tax_line.getDestinationValue())
    self.assertEquals(6, tax_line.getSourceCredit())

    income_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.income_account][0]
    self.assertEquals(self.expense_account,
                      income_line.getDestinationValue())
    self.assertEquals(30, income_line.getSourceCredit())

    # Of course, this invoice does not generate simulation again. New
    # applied rule is not created.
    related_applied_rule = related_invoice.getCausalityRelatedValue(
                                portal_type='Applied Rule')
    self.assertEquals(None, related_applied_rule)

    # and there's no other invoices
    self.assertEquals(1, len(self.portal.accounting_module.contentValues()))


  def test_tax_line_merged_build(self):
    # an order with 2 lines and 1 tax line will later be built in an invoice
    # with 2 lines and 1 tax line
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    resource2 = self.portal.product_module.newContent(
                            portal_type='Product',
                            title='Resource 2',
                            base_contribution_value_list=[base_1])
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setPriceCurrencyValue(self.currency)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line1 = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order_line2 = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=resource2,
                          quantity=7,
                          price=10,)
    self.commit()
    # check existing tax line
    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(2*15 + 7*10, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())

    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    self.tic()
    related_delivery = order.getCausalityRelatedValue(
                  portal_type=('Purchase Packing List', 'Sale Packing List'))
    self.assertNotEquals(related_delivery, None)
    related_delivery.setReady()
    related_delivery.start()
    related_delivery.stop()
    related_delivery.deliver()
    self.assertEquals('delivered', related_delivery.getSimulationState())
    self.tic()
    
    related_invoice = related_delivery.getCausalityRelatedValue(
                  portal_type=('Purchase Invoice Transaction',
                               'Sale Invoice Transaction'))
    self.assertNotEquals(related_invoice, None)
    invoice_line_list = related_invoice.contentValues(
                  portal_type='Invoice Line')
    tax_line_list = related_invoice.contentValues(
                  portal_type='Tax Line')

    self.assertEquals(2, len(invoice_line_list))

    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals([base_1], tax_line.getBaseApplicationValueList())
    self.assertEquals([], tax_line.getBaseContributionValueList())

    self.assertEquals('solved', related_invoice.getCausalityState())

  def test_tax_line_updated_on_invoice_line_change(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setPriceCurrencyValue(self.currency)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    self.tic()
    related_delivery = order.getCausalityRelatedValue(
                  portal_type=('Purchase Packing List', 'Sale Packing List'))
    self.assertNotEquals(related_delivery, None)
    related_delivery.setReady()
    related_delivery.start()
    related_delivery.stop()
    related_delivery.deliver()
    self.assertEquals('delivered', related_delivery.getSimulationState())
    self.tic()
    
    related_invoice = related_delivery.getCausalityRelatedValue(
                  portal_type=('Purchase Invoice Transaction',
                               'Sale Invoice Transaction'))
    self.assertNotEquals(related_invoice, None)
    self.assertEquals('solved', related_invoice.getCausalityState())
    invoice_line_list = related_invoice.contentValues(
                  portal_type='Invoice Line')
    tax_line_list = related_invoice.contentValues(
                  portal_type='Tax Line')

    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(30, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals([base_1], tax_line.getBaseApplicationValueList())
    self.assertEquals([], tax_line.getBaseContributionValueList())

    self.assertEquals(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]
    # change a total price on the invoice_line,
    invoice_line.setQuantity(3)
    self.tic()
    # it will be reflected on the tax line
    self.assertEquals(45, tax_line.getQuantity())
    self.assertTrue(tax_line.isDivergent())
    # and the invoice is diverged
    self.assertEquals('diverged', related_invoice.getCausalityState())
    

class TestTaxLineInvoiceSimulation(AccountingBuildTestCase):
  """Test Simulation of Tax Lines on Invoices
  """
  def test_tax_line_simulation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    invoice = self.order
    invoice.Order_applyTradeCondition(self.trade_condition, force=1)
    invoice.setSourceSectionValue(self.vendor)
    invoice.setSourceValue(self.vendor)
    invoice.setDestinationSectionValue(self.client)
    invoice.setDestinationValue(self.client)
    invoice.setStartDate(DateTime(2001, 1, 1))
    invoice.setPriceCurrencyValue(self.currency)
    invoice_line = invoice.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)
    tax_line_list = invoice.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]

    invoice.plan()
    invoice.confirm()
    invoice.start()
    self.assertEquals('started', invoice.getSimulationState())
    self.tic()
    related_applied_rule_list = invoice.getCausalityRelatedValueList(
                                      portal_type='Applied Rule')
    self.assertEquals(1, len(related_applied_rule_list))
    root_applied_rule = related_applied_rule_list[0]
    simulation_movement_list = root_applied_rule.contentValues(
                                   portal_type='Simulation Movement')
    self.assertEquals(2, len(simulation_movement_list))
    tax_simulation_movement_list = [m for m in simulation_movement_list
                                    if m.getOrderValue() == tax_line]
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]
    self.assertEquals([base_1],
        tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(100, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())
    self.assertEquals(self.currency,
                      tax_simulation_movement.getPriceCurrencyValue())

    invoice_simulation_movement_list = [m for m in simulation_movement_list
                                    if m.getOrderValue() == invoice_line]
    self.assertEquals(1, len(invoice_simulation_movement_list))
    invoice_simulation_movement = invoice_simulation_movement_list[0]
    self.assertEquals([base_1],
        invoice_simulation_movement.getBaseContributionValueList())
    self.assertEquals(10, invoice_simulation_movement.getQuantity())
    self.assertEquals(10, invoice_simulation_movement.getPrice())
    self.assertEquals(self.currency,
                      invoice_simulation_movement.getPriceCurrencyValue())
    self.assertEquals(self.resource,
                      invoice_simulation_movement.getResourceValue())

    accounting_line_list = invoice.getMovementList(
                            portal_type=('Sale Invoice Transaction Line',
                                         'Purchase Invoice Transaction Line'))
    self.assertEquals(3, len(accounting_line_list))
    receivable_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.receivable_account][0]
    self.assertEquals(self.payable_account,
                      receivable_line.getDestinationValue())
    self.assertEquals(120, receivable_line.getSourceDebit())
    
    tax_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.collected_tax_account][0]
    self.assertEquals(self.refundable_tax_account,
                      tax_line.getDestinationValue())
    self.assertEquals(20, tax_line.getSourceCredit())

    income_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.income_account][0]
    self.assertEquals(self.expense_account,
                      income_line.getDestinationValue())
    self.assertEquals(100, income_line.getSourceCredit())

    self.assertEquals('solved', invoice.getCausalityState())


class DiscountCalculation:
  """Test Discount Calculations
  """
  def test_simple_discount_model_line_calculation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    discount_model_line =self.trade_condition.newContent(
                    portal_type='Discount Model Line',
                    base_application_value=base_1,
                    float_index=1,
                    efficiency=0.2,
                    resource_value=self.discount)
  

class TestTaxLineCalculationSaleOrder(
    TestTaxLineCalculation, TestWithSaleOrder):
  pass

class TestTaxLineCalculationPurchaseOrder(
    TestTaxLineCalculation, TestWithPurchaseOrder):
  pass

class TestTaxLineCalculationSaleInvoice(
    TestTaxLineCalculation, TestWithSaleInvoice):
  def not_available(self):
    pass
  test_hierarchical_order_line_and_tax_line = not_available
  test_temp_order_hierarchical = not_available

class TestTaxLineCalculationPurchaseInvoice(
    TestTaxLineCalculation, TestWithPurchaseInvoice):
  def not_available(self):
    pass
  test_hierarchical_order_line_and_tax_line = not_available
  test_temp_order_hierarchical = not_available

class TestTaxLineOrderSimulationSaleOrder(
      TestTaxLineOrderSimulation, TestWithSaleOrder):
  pass

class TestTaxLineOrderSimulationPurchaseOrder(
      TestTaxLineOrderSimulation, TestWithPurchaseOrder):
  pass

class TestTaxLineInvoiceSimulationPurchaseInvoice(
      TestTaxLineInvoiceSimulation, TestWithPurchaseInvoice):
  pass

class TestTaxLineInvoiceSimulationSaleInvoice(
      TestTaxLineInvoiceSimulation, TestWithSaleInvoice):
  pass

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTaxLineCalculationSaleOrder))
  suite.addTest(unittest.makeSuite(TestTaxLineCalculationPurchaseOrder))
  suite.addTest(unittest.makeSuite(TestTaxLineCalculationSaleInvoice))
  suite.addTest(unittest.makeSuite(TestTaxLineCalculationPurchaseInvoice))
  suite.addTest(unittest.makeSuite(TestTaxLineOrderSimulationSaleOrder))
  suite.addTest(unittest.makeSuite(TestTaxLineOrderSimulationPurchaseOrder))
  suite.addTest(unittest.makeSuite(TestTaxLineInvoiceSimulationPurchaseInvoice))
  suite.addTest(unittest.makeSuite(TestTaxLineInvoiceSimulationSaleInvoice))
  return suite
