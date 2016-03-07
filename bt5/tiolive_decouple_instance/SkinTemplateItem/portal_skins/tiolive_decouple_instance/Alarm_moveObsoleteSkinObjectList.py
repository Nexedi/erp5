"""
 Decoupling the instance we need to move the Form used to create person
 and also the script used.

 Those objects are customized into portal_skins/express_customization
 and must be moved to tiolive_decouple_obsolete.

 The folder tiolive_decouple_obsolete is created only when it is required
 and it is not present into portal skins selection.
"""
from Products.ERP5Type.Log import log
portal = context.getPortalObject()
obsolete_object_list = ['Person_createUser',
                        'Person_viewCreateUserActionDialog']

express_customisation_folder = getattr(portal.portal_skins, "express_customisation", None)
if express_customisation_folder is None:
  express_customisation_folder = getattr(portal.portal_skins, "express_customisation_user_synchronization", None)
  if express_customisation_folder is None:
    return True

obsolete_skin_folder_id = "tiolive_decouple_obsolete"
obsolete_skin_folder = getattr(portal.portal_skins, obsolete_skin_folder_id, None)
if obsolete_skin_folder is None:
  portal.portal_skins.manage_addFolder(id=obsolete_skin_folder_id)

try:
  object_list = express_customisation_folder.manage_cutObjects(obsolete_object_list)
  portal.portal_skins[obsolete_skin_folder_id].manage_pasteObjects(object_list)
except AttributeError:
  log('FAILED to move %s to %s skin folder. Please check is the objects are already into %s.' % \
                          (obsolete_object_list, obsolete_skin_folder_id, obsolete_skin_folder_id))
  return False

return True
