request = container.REQUEST
selection_tool = context.portal_selections

if selection_tool.getSelectionInvertModeFor(selection_name):
  # if already in invert mode, toggle invert mode
  selection_tool.setSelectionInvertModeFor(selection_name, invert_mode=0)
else:
  # Set selection to currently checked items, taking into consideration changes
  # in uids
  selection_uids = selection_tool.getSelectionCheckedUidsFor(
                                  selection_name, REQUEST=request)
  filtered_uid_dict = {}
  listbox_uid = [int(x) for x in listbox_uid]
  uids = [int(x) for x in uids]
  for uid in uids:
    filtered_uid_dict[uid] = 1
  for uid in selection_uids:
    if uid in listbox_uid:
      if uid in uids:
        filtered_uid_dict[uid] = 1
    else:
      filtered_uid_dict[uid] = 1

  if len(filtered_uid_dict.keys()) > 0 :
    selection_tool.checkAll(selection_name, uids, REQUEST=None)
    selection_tool.setSelectionToIds(selection_name,
                              filtered_uid_dict.keys(), REQUEST=request)

url = selection_tool.getSelectionListUrlFor(
                        selection_name, REQUEST=request)
request.RESPONSE.redirect(url)
