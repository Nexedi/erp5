folder = context

activate_kw = {
  'tag': object_tag,
  'after_tag': folder_after_tag,
}
for key, value in activate_kw.items():
  if value is None:
    activate_kw.pop(key)

# Reindex folder immediately
folder.reindexObject(sql_catalog_id=sql_catalog_id)

folder_id = folder.getId()
if folder_after_tag is None:
  folder_after_tag = ()
bundle_tag = "%s_bundle_reindex" % folder_id
bundle_object_tag = "%s_reindex" % folder_id

# Spawn activities for bundles of content objects.
# Bundle size, in object count
BUNDLE_ITEM_COUNT=1000

def Folder_reindexObjectList(id_list_list):
  """
    Create an activity calling Folder_reindexObjectList.
  """
  folder.activate(activity='SQLQueue', priority=object_priority, 
                  **activate_kw).Folder_reindexObjectList(
     id_list=None,
     id_list_list=id_list_list,
     object_priority=object_priority,
     object_tag=object_tag,
     object_after_tag=object_after_tag,
     folder_tag=bundle_tag,
     folder_after_tag=bundle_object_tag,
     sql_catalog_id=sql_catalog_id,
  )
archive_test_script = getattr(context.getPortalObject(), "Archive_test", None)
try:
  tree_id_list = folder.getTreeIdList()
except (NotImplementedError, AttributeError):
  # Build a list of list, like this we parse ids only one time,
  # and then Folder_reinexObjectList will work with one list at
  # a time and remove it from the list of list
  # This id_list_list can be quite big and generate quite big
  # activities, but the effect is limited, because if we have too
  # much objects (like millions), we should use HBTree Folders, and
  # then the work will be splitted
  id_list = [x for x in folder.objectIds()]
  id_list_list = []
  for bundle_index in xrange(len(id_list) / BUNDLE_ITEM_COUNT):
    id_list_list.append(id_list[bundle_index * BUNDLE_ITEM_COUNT:((bundle_index + 1) * BUNDLE_ITEM_COUNT)])

  remaining_object_id_count = len(id_list) % BUNDLE_ITEM_COUNT
  if remaining_object_id_count > 0:
    id_list_list.append(id_list[-remaining_object_id_count:])
  Folder_reindexObjectList(id_list_list)
else:
  if archive_test_script is not None:
    new_tree_id_list = []
    for tree_id in tree_id_list:
      if folder.Archive_test(tree_id=tree_id, start_tree=start_tree, stop_tree=stop_tree):
        new_tree_id_list.append(tree_id)
    tree_id_list = new_tree_id_list
  else:
    if start_tree is not None:
      new_tree_id_list = []
      for tree_id in tree_id_list:
        if tree_id >= start_tree:
          new_tree_id_list.append(tree_id)
      tree_id_list = new_tree_id_list

    if stop_tree is not None:
      new_tree_id_list = []
      for tree_id in tree_id_list:
        if tree_id < stop_tree:
          new_tree_id_list.append(tree_id)
      tree_id_list = new_tree_id_list

  if len(tree_id_list) == 0:
    return

  i = 0

  tree_tag = "%s_tree" % folder_id

  # Say to Folder_reindexTreeObjectList to call himself again and
  # again until all tree_id_list are parsed. Also, make sure that
  # the work of the previous Folder_reindexTreeObjectList is completely
  # done
  tree_after_tag = folder_after_tag + (bundle_tag, bundle_object_tag)
  folder.activate(activity='SQLQueue', priority=object_priority, 
      after_tag=tree_after_tag, tag=tree_tag,
      ).Folder_reindexTreeObjectList(
    tree_id=None,
    tree_id_list=tree_id_list,
    folder_tag=bundle_tag,
    folder_after_tag=bundle_object_tag,
    object_priority=object_priority,
    sql_catalog_id=sql_catalog_id,
    object_tag=bundle_object_tag,
    tree_after_tag=tree_after_tag,
    tree_tag=tree_tag,
    )
  
  # Start an activity wich will wait the end of the module
  folder_id_after_tag =  folder_after_tag + (tree_tag, bundle_tag, bundle_object_tag)
  id_activate_kw = {}
  if object_tag is not None:
    id_activate_kw['tag'] = object_tag

  folder.activate(activity='SQLDict', priority=object_priority, 
                  after_tag=folder_id_after_tag, **id_activate_kw).getId()
