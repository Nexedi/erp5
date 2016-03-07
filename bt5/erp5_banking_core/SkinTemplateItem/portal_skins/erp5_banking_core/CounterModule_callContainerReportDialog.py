from DateTime import DateTime
node = context.REQUEST.form['vault']
default_resource = context.REQUEST.form['resource']
context.log("kw %s" %(kw,))
context.log("req %s" %(context.REQUEST.form,))
container_portal_type_list = ["Monetary Reception",]

base_price_dict = {}

if listbox is None:

#  node = context.getSource()
  reference_date = DateTime()
  container_list = []
  listbox = []
  #context.log("tracking list", context.portal_simulation.getCurrentTrackingList(at_date= reference_date, node = node))
  resource_translated_title_dict = {}
  total_price_dict = {}
  listbox_append = listbox.append
  for o in context.portal_simulation.getCurrentTrackingList(at_date= reference_date, node = node):
    cash_container = o.getObject()

    if cash_container.getParentValue().getPortalType()  in container_portal_type_list:
      # get one line in order to know some properties of the cash container
      container_dict = {}
      container_lines = cash_container.objectValues(portal_type='Container Line')
      if len(container_lines) == 0:
        context.log("MonetaryIssue_generateCashContainerInputDialog", "No container line find for cash container %s" %(cash_container.getRelativeUrl(),))
        continue
      container_line = container_lines[0]
      if default_resource is not None and container_line.getResourceId() != default_resource:
        context.log("skipping doc")
        continue
      container_dict['reference'] = cash_container.getReference()
      container_dict['cash_number_range_start'] = cash_container.getCashNumberRangeStart()
      container_dict['cash_number_range_stop'] = cash_container.getCashNumberRangeStop()

      resource = container_line.getResource()
      base_price = base_price_dict.get(resource, None)
      if base_price is None:
        base_price = container_line.getResourceValue().getBasePrice()
        base_price_dict[resource] = base_price
      container_dict['base_price'] = base_price
      resource_translated_title = resource_translated_title_dict.get(resource, None)
      if resource_translated_title is None:
        resource_translated_title = container_line.getResourceTranslatedTitle()
        resource_translated_title_dict[resource] = resource_translated_title
      container_dict['resource_translated_title'] = resource_translated_title
      quantity = container_line.getQuantity()
      container_dict['quantity'] = quantity
      total_price = total_price_dict.get((quantity,resource), None)
      if total_price is None:
        total_price = container_line.getTotalPrice(fast=0)
        total_price_dict[(quantity,resource)] = total_price
      container_dict['total_price'] = total_price
      container_dict['selection'] = 0
      container_dict['date'] = o.date
      container_dict['uid'] = 'new_%s' %(cash_container.getUid(),)   #cash_container.getReference().replace('/', '_'),)

      listbox_append(container_dict)

  def sortListbox(a, b):
    result = cmp(a["date"], b["date"])
    if result == 0:
      result = cmp(a["base_price"], b["base_price"])
      if result == 0:
        result = cmp(a["reference"], b["reference"])
      
    return result

  listbox.sort(sortListbox)

  context.Base_updateDialogForm(listbox=listbox
                                )

  return context.asContext(context=None
                           , portal_type=context.getPortalType()
                           ).CounterModule_viewContainerReportForm(**kw)
