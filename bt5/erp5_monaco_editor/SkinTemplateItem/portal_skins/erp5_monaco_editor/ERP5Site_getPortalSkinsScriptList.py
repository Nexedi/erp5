from Products.ERP5Type.Cache import CachingMethod
import json

def get_portal_skins_script():
  script_set = set()
  for skin_folder in context.getPortalObject().portal_skins.objectValues():
    script_set.update(
      skin_folder.objectIds(
        spec=['Script (Python)', 'External Method']
      )
    )
  return json.dumps(list(script_set))

return CachingMethod(
  get_portal_skins_script,
  id=(get_portal_skins_script),
  cache_factory='erp5_content_short',
)()
