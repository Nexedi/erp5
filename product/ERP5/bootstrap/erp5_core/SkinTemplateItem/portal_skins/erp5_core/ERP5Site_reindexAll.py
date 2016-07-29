portal = context.getPortalObject()
if clear_catalog:
  # clear the catalog before reindexing
  catalog = portal.portal_catalog.getSQLCatalog(sql_catalog_id)
  catalog.manage_catalogClear()

# disable alarms while we are reindexing
is_subscribed = portal.portal_alarms.isSubscribed()
if clear_catalog:
  if is_subscribed:
    portal.portal_alarms.unsubscribe()

# Reindex person module
print "#### Indexing person_module, stage 1 ####"
person_module=getattr(portal, 'person_module', None)
higher_priority = 1 + additional_priority
if person_module is not None :
  tag = 'person_stage_1'
  person_module.recurseCallMethod(
    method_id='immediateReindexObject',
    group_method_id='portal_catalog/catalogObjectList',
    method_kw={
      'sql_catalog_id': sql_catalog_id,
    },
    activate_kw={
      'tag': tag,
      'priority': higher_priority,
    },
    max_depth=1, # Do not reindex Person's subobjects
  )
    
print "#### Indexing translations ####"
context.ERP5Site_updateTranslationTable(sql_catalog_id=sql_catalog_id)

# Reindex categories
print "#### Indexing categories ####"
folder_tag = 'module'
folder_after_tag = ('person_stage_1', 'group_person_stage_1')
object_tag = 'category'
object_after_tag = folder_after_tag

context.portal_categories.activate(
                  tag=folder_tag,
                  priority=higher_priority,
                  after_tag=folder_after_tag).Folder_reindexAll(
                                         folder_tag=folder_tag,
                                         folder_after_tag=folder_after_tag,
                                         object_tag=object_tag,
                                         object_after_tag=object_after_tag,
                                         object_priority=higher_priority,
                                         sql_catalog_id=sql_catalog_id,
                                         start_tree=start_tree,
                                         stop_tree=stop_tree,)

print "#### Indexing alarms ####"
print "#### Indexing active results ####"
folder_tag = 'module'
folder_after_tag = ('category', 'person_stage_1', 'group_person_stage_1')
object_tag = 'document'
object_after_tag = folder_after_tag
object_priority = 2 + additional_priority
for folder in [context.portal_alarms, context.portal_activities]:
  folder.activate(
                    tag=folder_tag,
                    priority=object_priority,
                    after_tag=folder_after_tag).Folder_reindexAll(
                                           folder_tag=folder_tag,
                                           folder_after_tag=folder_after_tag,
                                           object_tag=object_tag,
                                           object_after_tag=object_after_tag,
                                           object_priority=object_priority,
                                           sql_catalog_id=sql_catalog_id,
                                           start_tree=start_tree,
                                           stop_tree=stop_tree,)

print "#### Indexing preferences ####"
preference_tag = 'portal_preferences'
context.portal_preferences.activate(
                    tag=preference_tag,
                    after_tag='category',
                    priority=additional_priority).Folder_reindexAll(
                                         folder_tag=preference_tag,
                                         object_tag=preference_tag,
                                         object_priority=additional_priority,
                                         sql_catalog_id=sql_catalog_id,
                                         start_tree=start_tree,
                                         stop_tree=stop_tree,)

# We index simulation first to make sure we can calculate tests
# (ie. related quantity)
print "#### Indexing simulation ####"
folder_tag = 'module'
folder_after_tag = ('category', 'document', 'person_stage_1', 'group_person_stage_1', preference_tag)
object_tag = 'simulation'
object_after_tag = folder_after_tag
object_priority = 3 + additional_priority
context.portal_simulation.activate(
                  tag=folder_tag,
                  priority=higher_priority,
                  after_tag=folder_after_tag).Folder_reindexAll(
                                         folder_tag=folder_tag,
                                         folder_after_tag=folder_after_tag,
                                         object_tag=object_tag,
                                         object_after_tag=object_after_tag,
                                         object_priority=higher_priority,
                                         sql_catalog_id=sql_catalog_id,
                                         start_tree=start_tree,
                                         stop_tree=stop_tree,)

# We index tools secondly
print "#### Indexing tools ####"

folder_tag = 'module'
folder_after_tag = ('category', 'person_stage_1', 'group_person_stage_1', preference_tag)
object_tag = 'document'
object_after_tag = folder_after_tag
object_priority = 2 + additional_priority
tool_list = [x for x in portal.objectValues() if \
             x.getUid != portal.getUid and \
             x.meta_type != 'ERP5 Folder' and \
             x.id not in ('portal_alarms', 'portal_activities', 'portal_classes', 'portal_preferences', 'portal_simulation', 'portal_uidhandler')]

for folder in tool_list:
  folder.activate(
                    tag=folder_tag,
                    priority=object_priority,
                    after_tag=folder_after_tag).Folder_reindexAll(
                                           folder_tag=folder_tag,
                                           folder_after_tag=folder_after_tag,
                                           object_tag=object_tag,
                                           object_after_tag=object_after_tag,
                                           object_priority=object_priority,
                                           sql_catalog_id=sql_catalog_id,
                                           start_tree=start_tree,
                                           stop_tree=stop_tree,)

# Then we index ERP5 Python Scripts
print "#### Indexing ERP5 Python Scripts ####"
for path, obj in portal.portal_skins.ZopeFind(portal.portal_skins, obj_metatypes=('ERP5 Python Script',), search_sub=1):
  obj.activate(tag=folder_tag,
               priority=object_priority,
               after_tag=folder_after_tag).immediateReindexObject(sql_catalog_id=sql_catalog_id)

# Then we index ERP5 SQL Methods
print "#### Indexing ERP5 SQL Methods ####"
for path, obj in portal.portal_skins.ZopeFind(portal.portal_skins, obj_metatypes=('ERP5 SQL Method',), search_sub=1):
  obj.activate(tag=folder_tag,
               priority=object_priority,
               after_tag=folder_after_tag).immediateReindexObject(sql_catalog_id=sql_catalog_id)

# Then we index everything except inventories
for folder in portal.objectValues(("ERP5 Folder",)):
  if folder.getId().find('inventory') < 0:
    print "#### Indexing contents inside folder %s ####" % folder.id
    folder.activate(
              tag=folder_tag,
              priority=object_priority,
              after_tag=folder_after_tag).Folder_reindexAll(
                                     folder_tag=folder_tag,
                                     folder_after_tag=folder_after_tag,
                                     object_tag=object_tag,
                                     object_after_tag=object_after_tag,
                                     object_priority=object_priority,
                                     sql_catalog_id=sql_catalog_id,
                                     start_tree=start_tree,
                                     stop_tree=stop_tree,)

# Then we index inventories
object_tag = 'inventory'
object_after_tag = ('module', 'category', 'person_stage_1', 'document', 'group_person_stage_1')
for folder in portal.objectValues(("ERP5 Folder",)):
  if folder.getId().find('inventory') >= 0: 
    print "#### Indexing contents inside folder %s ####" % folder.id
    folder.activate(
              tag=folder_tag,
              priority=object_priority,
              after_tag=folder_after_tag).Folder_reindexAll(
                                     folder_tag=folder_tag,
                                     folder_after_tag=folder_after_tag,
                                     object_tag=object_tag,
                                     object_after_tag=object_after_tag,
                                     object_priority=object_priority,
                                     sql_catalog_id=sql_catalog_id,
                                     start_tree=start_tree,
                                     stop_tree=stop_tree,)

# start activty from simulation because the erp5site is not an active object
context.portal_simulation.activate(
      after_tag=('inventory', 'simulation', 'person_stage_1', 'group_person_stage_1'),
      priority=3 + additional_priority
      ).InventoryModule_reindexMovementList(
                            sql_catalog_id=sql_catalog_id,
                            final_activity_tag='last_inventory_activity')

# restore alarm node 
if clear_catalog and is_subscribed:
  portal.portal_alarms.activate(after_tag=('inventory', 'module', 'inventory', 'simulation', 'person_stage_1',
                                           'group_person_stage_1', 'last_inventory_activity', 'document')).subscribe()

if final_activity_tag is not None:
  # Start a dummy activity which will get discarded when all started activities
  # (and all activities they trigger) are over.
  # Started on portal_simulation because activate does not work on portal object...
  # No idea if there is a better place.
  context.portal_simulation.activate(tag=final_activity_tag,
                                     priority=3 + additional_priority,
                                     after_tag=('module', 'inventory', 'simulation', 'person_stage_1',
                                                'group_person_stage_1', 'last_inventory_activity', 'document')
                                    ).getId()

return printed
