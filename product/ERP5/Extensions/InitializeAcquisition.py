from Products.ERP5.ERP5Globals import *
from Products.ERP5.Tool.Category import addBaseCategory
from Products.ERP5Type.Utils import convertToUpperCase

# This script defines init values for all base categories

def setBaseAcquisition(self):
  pc = self.portal_categories
  # Source and destination are defined by delivery, order, parent 
  #   we should not use causality here because of production reports
  #   for which source or destination can be None (ie. different from Production Order)
  for bc in ('source', 'destination',
             'target_source', 'target_destination',
             'source_section', 'destination_section', 
             'target_source_section', 'target_destination_section',):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList(('delivery', 'order', 'parent', ))
    pc[bc].setAcquisitionPortalTypeList(movement_or_item_or_delivery_or_order_or_invoice_type_list)
    pc[bc].setAcquisitionMaskValue(1)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
  # Other sources and destination are defined by delivery, order, parent or causality
  # None of those base categories should be set to None (incl. section)
  for bc in ('source_payment', 'destination_payment',
             'source_decision', 'destination_decision',
             'source_administration', 'destination_administration', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList(('delivery', 'order', 'parent', 'causality'))
    pc[bc].setAcquisitionPortalTypeList(movement_or_item_or_delivery_or_order_or_invoice_type_list)
    pc[bc].setAcquisitionMaskValue(1)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
  # Resource is defined by delivery, order or parent
  for bc in ('resource', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList(('delivery', 'order', 'parent'))
    pc[bc].setAcquisitionPortalTypeList(movement_or_item_or_delivery_or_order_or_invoice_type_list)
    pc[bc].setAcquisitionMaskValue(1)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
  # Coramy Specific for Variations
  for bc in ('coloris', 'taille', 'variante', 'morphologie' ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList(('delivery', 'order', 'parent', ))
    pc[bc].setAcquisitionPortalTypeList(movement_or_item_or_delivery_or_order_or_invoice_type_list)
    pc[bc].setAcquisitionMaskValue(1)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
  # Coramy Specific for Quantity Unit
  for bc in ('quantity_unit', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList(('delivery', 'order', 'parent', 'resource'))
    pc[bc].setAcquisitionPortalTypeList(
              movement_or_item_or_delivery_or_order_or_invoice_or_resource_type_list)
    pc[bc].setAcquisitionMaskValue(1)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
  # Add some useful bcs
  for bc in ('parent', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
  # Region acquisition
  for bc in ('region', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    pc[bc].setAcquisitionBaseCategoryList('subordination',)
    pc[bc].setAcquisitionPortalTypeList(['Address', 'Organisation', 'Person'])
    pc[bc].setAcquisitionMaskValue(1)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
    pc[bc].setAcquisitionObjectIdList(['default_address'])
  # Subordination acquisition
  for bc in ('subordination', ):
    if not hasattr(pc, bc):
      addBaseCategory(pc, bc)
    #pc[bc].setAcquisitionBaseCategoryList()
    pc[bc].setAcquisitionPortalTypeList(['Career', ])
    pc[bc].setAcquisitionMaskValue(0)
    pc[bc].setAcquisitionCopyValue(0)
    pc[bc].setAcquisitionAppendValue(0)
    pc[bc].setAcquisitionSyncValue(1)
    pc[bc].setAcquisitionObjectIdList(['default_career'])


  return '<html><body><p>Acquisition Done</p></body></html>'


