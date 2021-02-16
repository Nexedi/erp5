"""This script is called on the Invoice after the delivery builder has created
the new Invoice.
"""
if related_simulation_movement_path_list is None:
  raise RuntimeError('related_simulation_movement_path_list is missing. Update ERP5 Product.')

invoice = context

# set resource from price currency
#if not invoice.getResource():
#  invoice.setResource(invoice.getPriceCurrency())

related_packing_list = invoice.getDefaultCausalityValue()

# copy title, if not updating a new delivery
if not invoice.hasTitle() and related_packing_list.hasTitle():
  invoice.setTitle(related_packing_list.getTitle())

# initialize accounting_workflow to confirmed state
if invoice.getSimulationState() == 'draft':
  invoice.Delivery_confirm()
else:
  # call builder just same as after script of 'confirm' transition
  invoice.localBuild()
