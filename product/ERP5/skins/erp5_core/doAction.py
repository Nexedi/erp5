##parameters=action_select, form_id='', selection_index='', selection_name='', uids=None, listbox_uid=None

doAction = action_select.split()
doAction0 = doAction[0]
request = context.REQUEST

# First, update checked uids if uids is not None.
context.portal_selections.updateSelectionCheckedUidList(selection_name, uids=uids, listbox_uid=listbox_uid, REQUEST=request)

# If this is an object, a workflow or a folder, then jump to that view
if doAction0 in ('object', 'workflow', 'folder'):
  uri = ' '.join(doAction[1:])
  if uri.find('?') >= 0:
    uri += '&'
  else:
    uri += '?'
  uri += 'form_id=%s&selection_index=%s&selection_name=%s' % (form_id, selection_index, selection_name)
  if doAction0 == 'object':
    uri += '&dialog_category=object_action'
  return request.RESPONSE.redirect(uri)
# Otherwise, check if this is an automatic menu (add)
elif doAction0 == 'add':
  new_id = context.generateNewId()
  context.portal_types.constructContent(type_name=' '.join(doAction[1:]),
                           container=context,
                           id=str(new_id),
                           RESPONSE=request.RESPONSE)
  context[new_id].flushActivity(invoke=1)
  return request.RESPONSE

return getattr(context,form_id)(request)
