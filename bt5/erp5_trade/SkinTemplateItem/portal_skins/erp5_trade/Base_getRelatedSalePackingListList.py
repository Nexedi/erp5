portal = context.getPortalObject()
selection_name = context.REQUEST.form['selection_name']
uids = portal.portal_selections.getSelectionCheckedUidsFor(selection_name)

param_list = []
for uid in uids:
  param_list.append("child_resource_uid:list=%s" %(uid))

portal.sale_packing_list_module.Base_redirect('view?%s' %"&".join(param_list))
