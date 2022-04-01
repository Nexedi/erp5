uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)
if len(uids) == 0:
#   uids = map(lambda x:x.uid, context.portal_selections.callSelectionFor(selection_name))
  uids = [x.uid for x in context.portal_selections.callSelectionFor(selection_name)]
object_list =  list(context.portal_catalog(parent_uid=uids, portal_type = "Email"))
for o in object_list:
  o_value = o.getObject()
  if o is not None:
    print(o_value.getUrlString())

return printed
