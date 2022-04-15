from Products.CMFActivity.Errors import ActivityPendingError
Base_translateString = context.Base_translateString

person = context

default_career = None
if 'default_career' in person.objectIds():
  default_career = person['default_career']

if default_career is None:
  # No default career.
  message = Base_translateString('Current career must exist.')
  return context.Base_redirect(form_id=form_id,
                               selection_name=selection_name,
                               selection_index=selection_index,
                               keep_items={
                                  'portal_status_message': message,
                                  'portal_status_level': 'error',
                               })
else:
  # Copy and paste the default career.
  # Change IDs
  new_id = person.generateNewId()
  try:
    default_career.setId(new_id)
  except ActivityPendingError as error:
    message = Base_translateString("%s" % error)
    return context.Base_redirect(form_id=form_id,
                                 selection_name=selection_name,
                                 selection_index=selection_index,
                                 keep_items={
                                    'portal_status_message': message,
                                    'portal_status_level': 'error',
                                })
  new_start_date = default_career.getStopDate()

  cb_data = person.manage_copyObjects(ids=(new_id,))
  copied = person.manage_pasteObjects(cb_data)

  new_default_career = getattr(person, copied[0]['new_id'])

  new_default_career.edit(
    id='default_career',
    start_date=new_start_date,
    stop_date=None)

  message = Base_translateString('Last career step terminated. New career step added.')
  return context.Base_redirect(form_id=form_id,
                               selection_name=selection_name,
                               selection_index=selection_index,
                               keep_items={'portal_status_message': message})
