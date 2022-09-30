translate = context.Base_translateString
uids = kw.get('uids', [])
cancel_url = kw.get('cancel_url', None)
active_pad_relative_url = kw.get('active_pad_relative_url', None)
knowledge_pad = context.restrictedTraverse(active_pad_relative_url)
not_added_gadgets_mesage = None

selection_name = context.REQUEST.get('list_selection_name', None)
if selection_name is not None:
  # maybe user already selected them in a previous page in a listbox selection
  portal_selection = context.portal_selections
  params = portal_selection.getSelectionParamsFor(selection_name, {})
  uids.extend(params.get('uids', []))

if len(uids):
  for uid in uids:
    gadget = context.portal_catalog(uid=uid)[0]
    multiple_instances_allowed = getattr(gadget,'multiple_instances_allowed', 0)
    # check if exists already such box specialising this gadget
    if multiple_instances_allowed or not knowledge_pad.searchFolder(portal_type = 'Knowledge Box',
                                      validation_state = "!=deleted",
                                      specialise_uid = uid):
      # add as user has not added this gadget already
      knowledge_box = knowledge_pad.newContent(portal_type = 'Knowledge Box')
      knowledge_box.setSpecialiseValue(gadget)
      knowledge_box.visible()
    else:
      not_added_gadgets_mesage = "You already have such gadgets."
  msg = 'Gadget added.'
else:
  msg = 'Nothing to add.'

if not_added_gadgets_mesage is not None:
  msg = not_added_gadgets_mesage

translated_msg = context.Base_translateString(msg)
if cancel_url is not None:
  cancel_url = '%s?portal_status_message=%s' %(cancel_url,translated_msg)
  context.REQUEST.RESPONSE.redirect(cancel_url)
else:
  context.Base_redirect('view',
                        keep_items= {'portal_status_message':
                                     translated_msg})
