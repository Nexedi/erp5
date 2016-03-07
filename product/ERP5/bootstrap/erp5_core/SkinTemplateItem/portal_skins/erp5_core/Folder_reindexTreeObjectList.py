from Products.ERP5Type.Log import log
folder = context

# Keep compatibility with tree_id
if tree_id_list is not None:
  log('tree_id', tree_id)
  log('tree_id_list', tree_id_list)
  if tree_id is not None:
    raise ValueError, "both tree and tree_id_list should not be defined"
  tree_id = tree_id_list.pop()

# Spawn activities for bundles of content objects.
# Bundle size, in object count
BUNDLE_ITEM_COUNT = 1000

folder_id = folder.getId()
def Folder_reindexObjectList(id_list_list):
  """
    Create an activity calling Folder_reindexObjectList.
  """
  folder.activate(activity='SQLQueue', priority=object_priority, 
                  after_tag=object_tag,
                  tag=folder_tag).Folder_reindexObjectList(
     None,
     id_list_list=id_list_list,
     object_priority=object_priority,
     object_tag=object_tag,
     sql_catalog_id=sql_catalog_id,
     folder_tag=folder_tag,
     folder_after_tag=folder_after_tag,
  )

# HBTree folder
id_list = [x for x in folder.objectIds(base_id=tree_id)]
# Build a list of list, like this we parse ids only one time,
# and then Folder_reinexObjectList will work with one list at
# a time and remove it from the list of list
# This id_list_list can be quite big and generate quite big
# activities, but the effect is limited, because the work is
# splitted for each base_id of the HBTree.
id_list_list = []
for bundle_index in xrange(len(id_list) / BUNDLE_ITEM_COUNT):
  id_list_list.append(id_list[bundle_index * BUNDLE_ITEM_COUNT:((bundle_index + 1) * BUNDLE_ITEM_COUNT)])

remaining_object_id_count = len(id_list) % BUNDLE_ITEM_COUNT
if remaining_object_id_count > 0:
  id_list_list.append(id_list[-remaining_object_id_count:])
Folder_reindexObjectList(id_list_list=id_list_list)

if tree_id_list is not None:
  if len(tree_id_list) > 0:
    # Calling again and again the same script allow to decrease the
    # number of activities by the same time and increase performance.
    folder.activate(activity='SQLQueue', priority=object_priority,
      after_tag=tree_after_tag, 
      tag=tree_tag).Folder_reindexTreeObjectList(
        tree_id=None,
        tree_id_list=tree_id_list,
        folder_tag=folder_tag,
        folder_after_tag=folder_after_tag,
        object_priority=object_priority,
        sql_catalog_id=sql_catalog_id,
        object_tag=object_tag,
        tree_after_tag=tree_after_tag,
        tree_tag=tree_tag,
        )
