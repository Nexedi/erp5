request = context.REQUEST
stool = context.portal_selections

if stool.getSelectionInvertModeFor(selection_name):
  # if already in invert mode, toggle invert mode
  stool.setSelectionInvertModeFor(selection_name, invert_mode=0)
else:
  # Set selection to currently checked items, taking into consideration changes
  # in uids
  selection_uids = stool.getSelectionCheckedUidsFor(
                                  selection_name, REQUEST=request)
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

  if len(filtered_uid_dict.keys()) > 0 :
    stool.checkAll(selection_name, uids, REQUEST=None)
    stool.setSelectionToIds(selection_name,
                              filtered_uid_dict.keys(), REQUEST=request)

url = stool.getSelectionListUrlFor(
                        selection_name, REQUEST=request)
request.RESPONSE.redirect(url)
