portal_type = context.getPortalType()
return context.Delivery_saveContainerFastInputLine(
  listbox=listbox,
  line_portal_type=portal_type + ' Line',
  container_line_portal_type=portal_type + ' Container',
)
