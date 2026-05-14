from Products.ERP5Type.Cache import CachingMethod
import json

portal = context.getPortalObject()

def get_autoconplete_word_list():
  full_word_list = ['context', 'portal', 'self', 'traverse', 'restrictedTraverse', 'REQUEST', 'RESPONSE', 'searchFolder']
  script_set = set()
  for skin_folder in context.getPortalObject().portal_skins.objectValues():
    script_set.update(
      skin_folder.objectIds(
        spec=['Script (Python)', 'External Method']
      )
    )
  full_word_list += list(script_set)
  full_word_list += [portal_type_row.id.lower().replace(' ', '_') for portal_type_row in portal.portal_types.searchFolder()]
  return json.dumps(" ".join(full_word_list))

return CachingMethod(
  get_autoconplete_word_list,
  id=(get_autoconplete_word_list),
  cache_factory='erp5_content_short',
)()
