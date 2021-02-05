from random import getrandbits
portal = context.getPortalObject()
if clear_catalog:
  portal.portal_catalog.getSQLCatalog(sql_catalog_id).manage_catalogClear()

# disable alarms while we are reindexing
is_subscribed = portal.portal_alarms.isSubscribed()
if clear_catalog and is_subscribed:
  portal.portal_alarms.unsubscribe()

base_tag = '%s_%x_' % (script.id, getrandbits(32))
user_tag = base_tag + 'person_stage_1'
category_tag = base_tag + 'category'
document_tag = base_tag + 'document'
preference_tag = base_tag + 'portal_preferences'
simulation_tag = base_tag + 'simulation'
inventory_tag = base_tag + 'inventory'
last_inventory_tag = base_tag + 'last_inventory_activity'
def reindex(document_list, tag, after_tag):
  for document in document_list:
    print '#### Indexing', document.id, '####'
    document.activate(
      priority=additional_priority,
      tag=tag,
      after_tag=after_tag,
    ).recursiveReindexObject(
      activate_kw={
        'tag': tag,
        'priority': additional_priority,
      },
      sql_catalog_id=sql_catalog_id,
    )
  return printed

# XXX: Must be replaced by an in-ZODB mapping from user_id to any type of user
# documents (not just Persons), otherwise catalog risks undergoing a
# security_uid explosion if many users (ex: persons) have local roles on
# documents (ex: persons) granting them View permission but the user is not
# indexed before corresponding document is.
print "#### Indexing person_module, stage 1 ####"
person_module = getattr(portal, 'person_module', None)
if person_module is not None:
  person_module.recurseCallMethod(
    method_id='immediateReindexObject',
    method_kw={
      'sql_catalog_id': sql_catalog_id,
    },
    activate_kw={
      'group_method_id': 'portal_catalog/catalogObjectList',
      'tag': user_tag,
    },
    max_depth=1, # Do not reindex Person's subobjects
  )
print "#### Indexing translations ####"
portal.ERP5Site_updateTranslationTable(sql_catalog_id=sql_catalog_id)
print reindex(
  [portal.portal_categories],
  tag=category_tag,
  after_tag=user_tag,
),
print reindex(
  [portal.portal_alarms, portal.portal_activities],
  tag=document_tag,
  after_tag=(user_tag, category_tag),
),
print reindex(
  [portal.portal_preferences],
  tag=preference_tag,
  after_tag=(user_tag, category_tag),
),
# Simulation is needed to calculate tests (ie. related quantity)
print reindex(
  [portal.portal_simulation],
  tag=simulation_tag,
  after_tag=(user_tag, category_tag, document_tag, preference_tag),
),
print reindex(
  [
    x for x in portal.objectValues()
    if x.getUid != portal.getUid and
      x.id not in (
        'portal_alarms',
        'portal_activities',
        'portal_categories',
        'portal_classes',
        'portal_preferences',
        'portal_simulation',
      ) and
      'inventory' not in x.id
  ],
  tag=document_tag,
  after_tag=(user_tag, category_tag, preference_tag),
),
# Then we index ERP5 Python Scripts and ERP5 Form - this is fundamentally broken and will go away, do not depend on it !
skin_activate_kw = {
  'tag': document_tag,
  'priority': additional_priority,
  'after_tag': (user_tag, category_tag, preference_tag),
}
for _, obj in portal.portal_skins.ZopeFind(portal.portal_skins, obj_metatypes=('ERP5 Python Script', 'ERP5 Form', 'ERP5 Report'), search_sub=1):
  obj.recursiveReindexObject(activate_kw=skin_activate_kw,
                             sql_catalog_id=sql_catalog_id)
print reindex(
  [
    x for x in portal.objectValues(("ERP5 Folder", ))
    if 'inventory' in x.id
  ],
  tag=inventory_tag,
  after_tag=(user_tag, category_tag, document_tag, preference_tag),
),

portal.portal_activities.activate(
  after_tag=(user_tag, category_tag, document_tag, preference_tag, inventory_tag, simulation_tag),
).InventoryModule_reindexMovementList(
  sql_catalog_id=sql_catalog_id,
  final_activity_tag=last_inventory_tag,
)

# restore alarm node 
if clear_catalog and is_subscribed:
  portal.portal_alarms.activate(
    after_tag=(user_tag, category_tag, document_tag, preference_tag, inventory_tag, simulation_tag, last_inventory_tag),
  ).subscribe()

portal.portal_activities.activate(
  tag=final_activity_tag,
  after_tag=(user_tag, category_tag, document_tag, preference_tag, inventory_tag, simulation_tag, last_inventory_tag),
).getId()
return printed
