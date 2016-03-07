folder = context

# Keep compatibility with id_list
if id_list_list is not None:
  if id_list is not None:
    raise ValueError, "both id_list and id_list_list can be defined"
  if len(id_list_list) == 0:
    return None
  id_list = id_list_list.pop()

activate_kw = {
  'tag': object_tag,
  'after_tag': object_after_tag,
  'priority': object_priority
}
for key, value in activate_kw.items():
  if value is None:
    activate_kw.pop(key)

for id in id_list:
  obj = getattr(folder, id, None)
  if obj is not None:
    obj.recursiveReindexObject(activate_kw=activate_kw,
                               sql_catalog_id=sql_catalog_id)


if id_list_list is not None:
  if len(id_list_list) > 0:
    if count is None:
      count = 1
    new_activity_kw = {}
    # We do not want to wait until there is enough activities
    # So add BUNDLE_ITEM_COUNT * node_len activities before waiting
    node_len = len(context.portal_activities.getProcessingNodeList())
    if count % node_len == 0:
      new_activity_kw['after_tag'] = folder_after_tag
      count = 0
    count += 1

    # By calling again and again, we improve performance and we have
    # less activities by the same time
    folder.activate(activity='SQLQueue',
      priority=object_priority,
      tag=folder_tag, **new_activity_kw).Folder_reindexObjectList(
         None,
         id_list_list=id_list_list,
         object_priority=object_priority,
         object_tag=object_tag,
         sql_catalog_id=sql_catalog_id,
         folder_tag=folder_tag,
         folder_after_tag=folder_after_tag,
         count=count,
      )
