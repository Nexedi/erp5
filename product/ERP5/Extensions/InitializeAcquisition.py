from Products.ERP5.ERP5Globals import *
from Products.ERP5.Tool.Category import addBaseCategory

# This script defines init values for all base categories

def setBaseAcquisition(self):
  pc = self.portal_categories
  # Source and destination are defined by delivery, order, parent or causality
  for bc in ('source', 'destination',
             'source_section', 'destination_section',
             'source_payment', 'destination_payment',
             'source_decision', 'destination_decision',
             'source_administration', 'destination_administration', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList(('delivery', 'order', 'parent', 'causality'))
    pc[bc].setAcquisitionPortalTypeList(movement_or_item_or_delivery_or_order_or_invoice_type_list)
    pc[bc].setAcquisitionMaskValue(0)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
  # Resource is defined by delivery, order or parent
  for bc in ('resource', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList(('delivery', 'order', 'parent'))
    pc[bc].setAcquisitionPortalTypeList(movement_or_item_or_delivery_or_order_or_invoice_type_list)
    pc[bc].setAcquisitionMaskValue(0)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
  # Coramy Specific for Variations
  for bc in ('coloris', 'taille', 'variante', 'morphologie' ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList(('delivery', 'order', 'parent', ))
    pc[bc].setAcquisitionPortalTypeList(movement_or_item_or_delivery_or_order_or_invoice_type_list)
    pc[bc].setAcquisitionMaskValue(0)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
  # Coramy Specific for Quantity Unit
  for bc in ('quantity_unit', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList(('delivery', 'order', 'parent', 'resource'))
    pc[bc].setAcquisitionPortalTypeList(
              movement_or_item_or_delivery_or_order_or_invoice_or_resource_type_list)
    pc[bc].setAcquisitionMaskValue(0)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
  # Add some useful bcs
  for bc in ('parent', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)

  return '<html><body><p>Acquisition Done</p></body></html>'


