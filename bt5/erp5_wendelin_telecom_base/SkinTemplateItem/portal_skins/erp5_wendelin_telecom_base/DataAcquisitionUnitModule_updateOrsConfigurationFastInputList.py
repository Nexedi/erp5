portal = context.getPortalObject()

for listbox_item in listbox:
  if 'listbox_key' in listbox_item:
    data_acquisition_unit_url = listbox_item['listbox_key']
    title = listbox_item['title']
    destination_project = listbox_item['destination_project']

    data_acquisition_unit = portal.restrictedTraverse(data_acquisition_unit_url)
    data_acquisition_unit.setTitle(title)

    data_supply = data_acquisition_unit.DataAcquisitionUnit_getOrsDataSupply()
    # Non-standard ORS Data Acquisition Unit
    if data_supply is None:
      portal_status_message = "No related Data Supply found for %s." \
        % data_acquisition_unit.getReference()
      kw['keep_items'] = dict(
        portal_status_message=portal_status_message,
        portal_status_level='error'
      )
      return context.Base_redirect('view', **kw)

    data_supply.setDestinationProject(destination_project)

return context.Base_redirect('view', keep_items={
  'portal_status_message': 'ORS configurations successfully updated.'
})
