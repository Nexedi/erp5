"""
  This script will redirect (HTTP redirect) to respective ERP5 Person object by reference.
  This script is used in "NO ZODB" approach mode although it can be used in other UI parts
  as well.
"""
person = context.Base_getUserValueByUserId(reference)
if person is not None:
  person.Base_redirect(form_id='view')
else:
  # logged in user (or anonymous) can't access or no such user exists
  context.Base_redirect(
    form_id = 'view',
    keep_items = {'portal_status_message':
                     context.Base_translateString('You can not access person object.')})
