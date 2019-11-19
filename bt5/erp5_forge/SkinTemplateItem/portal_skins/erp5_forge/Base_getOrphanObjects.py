from Products.ERP5Type.Document import newTempBase

## Stuff that is ignored
#- everything that is not in a portal_*
#- portal_trash, portal_categories, portal_templates, portal_preferences
#- objects whose meta-type is 'External Method' or 'Filesystem*'
#- 'portal_skins/external_method' & 'portal_skins/custom'
#- 'portal_workflow/business_template_building_workflow' & 'portal_workflow/business_template_installation_workflow'
#- 'portal_catalog/erp5_mysql' & 'portal_catalog/cps3_mysql' & 'portal_types/Business Template'
##

portals_scanned = ['portal_actions', 'portal_memberdata', 'portal_skins', 'portal_types', 'portal_undo', 'portal_url', 'portal_workflow',  'portal_membership', 'portal_registration', 'portal_report', 'portal_rules', 'portal_ids', 'portal_simulation', 'portal_alarms', 'portal_domains', 'portal_deliveries', 'portal_orders', 'portal_catalog', 'portal_selections', 'portal_synchronizations', 'portal_activities']
orphans_list = []
if object is None:
  object = context
objects = object.objectValues()
for o in objects:
  object_path = '/'.join(o.getPhysicalPath()[2:])
  if 'portal_skins/external_method' in object_path or \
     'portal_skins/custom' in object_path or \
     'portal_workflow/business_template_building_workflow' in object_path or \
     'portal_workflow/business_template_installation_workflow' in object_path or \
     'portal_catalog/erp5_mysql' in object_path or \
     'portal_catalog/cps3_mysql' in object_path or\
     'portal_types/Business Template' in object_path:
    continue
  if (object is not context) or (object_path.split('/')[0] in portals_scanned):
    if not o.meta_type.startswith('Filesystem') and o.meta_type != 'External Method':
      context.log("lol", object_path)
      if not context.getPortalObject().Base_getOriginalBusinessTemplateId(file=object_path):
        if object_path not in portals_scanned:
          # orphan object
          orphans_list.append(object_path)
      # Recursively check children
      orphans_list.extend([x.uid for x in context.Base_getOrphanObjects(object=o)])

object_list = []
for orphan in orphans_list:
  my_dict = {}
  my_dict['uid'] = orphan
  temp_object = newTempBase(folder=context.getPortalObject(), id='1234')
  temp_object.edit(**my_dict)
  object_list.append(temp_object)

return object_list
