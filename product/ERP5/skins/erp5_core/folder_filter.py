##parameters=selection_name, uids=[], listbox_uid=[]


request = context.REQUEST

# Set selection to currently checked items, taking into consideration changes in uids
selection_uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name, REQUEST=request)
filtered_uid_dict = {}
listbox_uid = map(lambda x:int(x), listbox_uid)
uids = map (lambda x:int(x), uids)
for uid in uids:
   filtered_uid_dict[uid] = 1
for uid in selection_uids:
  if uid in listbox_uid:
    if uid in uids:
      filtered_uid_dict[uid] = 1
  else:
    filtered_uid_dict[uid] = 1
context.portal_selections.checkAll(selection_name, uids, REQUEST=None)
context.portal_selections.setSelectionToIds(selection_name, filtered_uid_dict.keys(), REQUEST=request)
url = context.portal_selections.getSelectionListUrlFor(selection_name, REQUEST=request)

request.RESPONSE.redirect(url)
