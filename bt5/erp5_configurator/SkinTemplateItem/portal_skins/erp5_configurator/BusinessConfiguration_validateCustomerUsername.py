# check that customer did not enter in form repeating user names
reference_list = REQUEST.get('_original_field_your_reference', [])
for reference in reference_list:
  if reference_list.count(reference) != 1:
    # customer entered in form repeating user names
    return 0

portal = context.getPortalObject()
reference = editor

# check this is a not a reference from acl_user
if portal.acl_users.searchUsers(login=reference, exact_match=True):
    return 0

# first check if a Business Configuration has not already "reserved" it
# through a Person Configuration Item which when build will create a real
# Nexedi ERP5 account.

bc_key = REQUEST.get('business_configuration_key', None)
bc_path = None
if bc_key is None:
  configuration_save = portal.restrictedTraverse(REQUEST.get('configuration_save_url'))
  if configuration_save is not None:
    bc_key = configuration_save.getParentValue().getRelativeUrl()

if bc_key is not None:
  bc_path = "NOT %%/%s/%%" % bc_key

if portal.portal_catalog.getResultValue(
                         reference = reference,
                         portal_type='Person Configurator Item',
                         path = bc_path) is not None:
  return 0

return 1
