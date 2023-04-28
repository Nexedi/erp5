# Inventory requires reindexing when older movements become available, because
# inventory generates deltas against the past stock, using a catalog. It is only
# necessary to reindex Inventory documents instead of Inventory movements, because
# Inventory reindexes its movements in a special way to the stock table by itself.
#
# FIXME: I think it would be better to replace this script with a good interactor
# which reindexes future inventory documents.

previous_tag = None
portal = context.getPortalObject()
portal_type_list = portal.getPortalInventoryTypeList()
if not portal_type_list:
  return

# We have to reindex all inventory documents in the order of the dates.
# Uids are used to make the ordering consistent, even when multiple documents have
# the same date.
for inventory in portal.portal_catalog(portal_type=portal_type_list,
                                       limit=None,
                                       sort_on=[('delivery.start_date', 'ascending'), ('uid', 'ascending')],
                                       sql_catalog_id=sql_catalog_id):
  inventory = inventory.getObject()
  tag = 'inventory_%i' % inventory.getUid()
  activate_kw = {'tag': tag}
  if previous_tag is not None:
    activate_kw['after_tag'] = previous_tag
  previous_tag = tag
  inventory.reindexObject(activate_kw=activate_kw, sql_catalog_id=sql_catalog_id)

if final_activity_tag is not None and previous_tag is not None:
  # Dummy activity used to determine if the previously started activities are over.
  context.activate(activity='SQLDict', tag=final_activity_tag, after_tag=previous_tag).getId()
