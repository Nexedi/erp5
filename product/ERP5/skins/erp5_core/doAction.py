##parameters=action_select, form_id='', selection_index='', selection_name='', uids=None, listbox_uid=None

import string

doAction = action_select.split()
doAction0 = doAction[0]
request = context.REQUEST

# First, update checked uids if uids is not None.
context.portal_selections.updateSelectionCheckedUidList(selection_name, uids=uids, listbox_uid=listbox_uid, REQUEST=request)

# If single word, then jump to that view
if len(doAction) == 1:
  if doAction0.find('?') >= 0:
    return request.RESPONSE.redirect('%s&form_id=%s&selection_index=%s&selection_name=%s' % (doAction0, form_id, selection_index, selection_name))
  else:
    return request.RESPONSE.redirect('%s?form_id=%s&selection_index=%s&selection_name=%s' % (doAction0, form_id, selection_index, selection_name))
# Otherwise, check if this is an automatic menu (add)
elif doAction0 == 'add':
  new_id = context.generateNewId()
  context.portal_types.constructContent(type_name=string.join(doAction[1:],' '),
                           container=context,
                           id=str(new_id),
                           RESPONSE=request.RESPONSE)
  context[new_id].flushActivity(invoke=1)
  return request.RESPONSE

return getattr(context,form_id)(request)
