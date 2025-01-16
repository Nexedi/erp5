portal = context.getPortalObject()

# hardcode form id to make sure we get the correct ME
form_id = 'ManufacturingExecutionModule_viewManufacturingExecutionList'
form = getattr(context, form_id, None)

if form:
  listbox = form.Base_getListbox()
  selection_name = listbox.get_value('selection_name')
  if selection_name:
    uids = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)
    if len(uids):
      selection_params = dict(uid=uids)
    else:
      selection_params = portal.portal_selections.getSelectionParamsFor(selection_name)
    selection_params.update(
      {
        'simulation_state': ('started', 'stopped'),
        'strict_ledger_uid': portal.portal_categories.ledger.manufacturing.execution.getUid()
      })

    return portal.portal_catalog(**selection_params)
return []
