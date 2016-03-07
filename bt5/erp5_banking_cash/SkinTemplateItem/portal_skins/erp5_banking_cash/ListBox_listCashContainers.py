from zExceptions import Redirect
def error(msg):
  raise Redirect('%s/view?portal_status_message=%s' % (
    context.absolute_url(),
    context.Base_translateString(msg))
  )

node = context.getBaobabSource()
if node is None:
  error('Please select a source')
if context.getPortalType() == 'Cash Movement New Not Emitted' and 'transit' not in node:
  error('Transit must be in source.')
at_date = context.getStartDate()
if at_date is None:
  error('Please register a date.')

tracking_kw = {
  'at_date': at_date,
  'node': node,
  'limit_expression': (int(kw.get('list_start', 0)), int(kw.get('list_lines', 20))),
}

request = context.REQUEST
reference = getattr(request, 'your_reference', None)
if reference:
  tracking_kw['reference'] = reference

container_portal_type_set = {
  'Monetary Reception': None,
}
listbox = []
append = listbox.append
for o in context.portal_simulation.getCurrentTrackingList(**tracking_kw):
  cash_container = o.getObject()
  if cash_container.getParentValue().getPortalType() not in container_portal_type_set:
    continue
  container_line_list = cash_container.objectValues(portal_type='Container Line')
  if len(container_line_list) == 0:
    # XXX: we should probably raise here instead
    continue
  container_line = container_line_list[0]
  append({
    'uid': cash_container.getUid(),
    'reference': cash_container.getReference(),
    'cash_number_range_start': cash_container.getCashNumberRangeStart(),
    'cash_number_range_stop': cash_container.getCashNumberRangeStop(),
    'date': o.date,
    'resource_translated_title': container_line.getResourceTranslatedTitle(),
    'quantity': container_line.getQuantity(),
    'total_price': container_line.getTotalPrice(fast=0),
  })
context.Base_updateDialogForm(listbox=listbox)
return context.ListBox_initializeFastInput()
