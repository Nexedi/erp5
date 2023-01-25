'''
  this script is the conductor. All other scripts that permit to create a
  paysheet are called here
'''

# Delete all objects in the paysheet
id_list = []
for paysheet_item in context.objectValues(portal_type= \
  ['Pay Sheet Transaction Line', 'Pay Sheet Line']):
  # Delete lines which now became outdated and keep the sub-objects
  id_list.append(paysheet_item.getId())
context.manage_delObjects(id_list)

# create Pay Sheet Lines
context.createPaySheetLineList(listbox=listbox)

if not('skip_redirect' in kw and kw['skip_redirect'] == True):
  # Return to pay sheet default view
  from ZTUtils import make_query
  redirect_url = '%s/%s?%s' % (context.absolute_url(), 'view', make_query())
  return context.REQUEST.RESPONSE.redirect(redirect_url)
