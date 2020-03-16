"""This script is called on the Invoice after the delivery builder has created
the new Invoice.
"""

if related_simulation_movement_path_list is None:
  raise RuntimeError, 'related_simulation_movement_path_list is missing. Update ERP5 Product.'

invoice = context

# if installed erp5_simplified_invoicing, set resource from price currency
if not invoice.Invoice_isAdvanced():
  if not invoice.getResource():
    invoice.setResource(invoice.getPriceCurrency())

related_packing_list = invoice.getDefaultCausalityValue()
related_order = None if related_packing_list is None else \
  related_packing_list.getDefaultCausalityValue()

# copy payment conditions from packing list
# if missing, try to copy from order (for compatibility)
if not invoice.contentValues(portal_type='Payment Condition'):
  payment_condition_copy_id_list = []
  if related_packing_list is not None:
    payment_condition_copy_id_list = related_packing_list.contentIds(filter={'portal_type':'Payment Condition'})
  if len(payment_condition_copy_id_list) > 0:
    clipboard = related_packing_list.manage_copyObjects(ids=payment_condition_copy_id_list)
    invoice.manage_pasteObjects(clipboard)
  elif related_order is not None:
    payment_condition_copy_id_list = related_order.contentIds(
      filter={'portal_type':'Payment Condition'})
    if len(payment_condition_copy_id_list) > 0:
      clipboard = related_order.manage_copyObjects(ids=payment_condition_copy_id_list)
      invoice.manage_pasteObjects(clipboard)

# copy title, if not updating a new delivery
if not invoice.hasTitle() and related_packing_list is not None and \
   related_packing_list.hasTitle():
  invoice.setTitle(related_packing_list.getTitle())

# initialize accounting_workflow to confirmed state
if invoice.getSimulationState() == 'draft':
  invoice.Delivery_confirm()
else:
  # call builder just same as after script of 'confirm' transition
  invoice.localBuild()
