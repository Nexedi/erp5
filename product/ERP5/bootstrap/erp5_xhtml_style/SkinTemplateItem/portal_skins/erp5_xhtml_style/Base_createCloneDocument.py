"""
  Create new Document by cloning an existing document
  or by creating a new document.

  Pretty messages are provided to the user.
"""
portal = context.getPortalObject()
translateString =  portal.Base_translateString
form_data = portal.REQUEST.form

if clone:
  portal_type = context.getPortalType()
else:
  portal_type = form_data['clone_portal_type']

# We copy contents in place if possible
try:
  source = context.aq_explicit.original_container
except AttributeError:
  source = context.getParentValue()
if destination is None:
  destination = source
if not (portal_type in destination.getVisibleAllowedContentTypeList() and
        portal.portal_membership.checkPermission('Copy or Move', context)):
  if batch_mode:
    return None
  else:
    return context.Base_redirect(keep_items={'portal_status_message':
             translateString("You are not allowed to clone this object.")})

# prepare query params
kw = {'portal_type' : translateString(portal_type)}

if web_mode:
  script = getattr(context, "Base_checkCloneConsistency", None)
  if script is not None:
    msg = script(**form_data)
    if msg is not None:
      return context.Base_redirect(form_id, 
                          editable_mode=editable_mode,
                          keep_items={'portal_status_message': msg})

# Standard cloning method
if clone:
  # Copy and paste the object
  try:
    original_id = context.aq_explicit.original_id
  except AttributeError:
    original_id = context.getId()
  # This is required for objects acquired in Web Section
  clipboard = source.manage_copyObjects(ids=[original_id])
  context.REQUEST.set('__cp', clipboard) # CopySupport is using this to set
                           # tracebility information in edit_workflow history
  paste_result = destination.manage_pasteObjects(cb_copy_data=clipboard)
  new_object = destination[paste_result[0]['new_id']]
  message_kind = 'Clone'
else:
  new_object = destination.newContent(portal_type=portal_type)
  message_kind = 'New'

if web_mode:
  # Edit the objects with some properties
  # Define a list of field name to take into account in the cloning process
  ACCEPTABLE_FORM_ID_LIST = [ 'clone_reference' , 'clone_language'
                             , 'clone_version' , 'clone_revision'
                             , 'clone_title' , 'clone_short_title' ] 

  # Set properties to the new object
  edit_kw = {}
  property_id_list = new_object.propertyIds()
  for (key, val) in list(form_data.items()):
    if key in ACCEPTABLE_FORM_ID_LIST and key[len('clone_'):] in property_id_list:
      edit_kw[key[len('clone_'):]] = val
  new_object.edit(**edit_kw)

if batch_mode:
  return new_object
else:
  if web_mode and not editable_mode: 
    form_id = 'view'
  msg = translateString("Created %s ${portal_type}." % message_kind, mapping = kw)
  return new_object.Base_redirect(form_id, 
                                  editable_mode=1,
                                  keep_items={'portal_status_message': msg})
