<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string encoding="cdata"><![CDATA[

from Products.ERP5Type.Log import log\n
folder = context\n
\n
# Keep compatibility with tree_id\n
if tree_id_list is not None:\n
  log(\'tree_id\', tree_id)\n
  log(\'tree_id_list\', tree_id_list)\n
  if tree_id is not None:\n
    raise ValueError, "both tree and tree_id_list should not be defined"\n
  tree_id = tree_id_list.pop()\n
\n
# Spawn activities for bundles of content objects.\n
# Bundle size, in object count\n
BUNDLE_ITEM_COUNT = 1000\n
\n
folder_id = folder.getId()\n
def Folder_reindexObjectList(id_list_list):\n
  """\n
    Create an activity calling Folder_reindexObjectList.\n
  """\n
  folder.activate(activity=\'SQLQueue\', priority=object_priority, \n
                  after_tag=object_tag,\n
                  tag=folder_tag).Folder_reindexObjectList(\n
     None,\n
     id_list_list=id_list_list,\n
     object_priority=object_priority,\n
     object_tag=object_tag,\n
     sql_catalog_id=sql_catalog_id,\n
     folder_tag=folder_tag,\n
     folder_after_tag=folder_after_tag,\n
  )\n
\n
# HBTree folder\n
id_list = [x for x in folder.objectIds(base_id=tree_id)]\n
# Build a list of list, like this we parse ids only one time,\n
# and then Folder_reinexObjectList will work with one list at\n
# a time and remove it from the list of list\n
# This id_list_list can be quite big and generate quite big\n
# activities, but the effect is limited, because the work is\n
# splitted for each base_id of the HBTree.\n
id_list_list = []\n
for bundle_index in xrange(len(id_list) / BUNDLE_ITEM_COUNT):\n
  id_list_list.append(id_list[bundle_index * BUNDLE_ITEM_COUNT:((bundle_index + 1) * BUNDLE_ITEM_COUNT)])\n
\n
remaining_object_id_count = len(id_list) % BUNDLE_ITEM_COUNT\n
if remaining_object_id_count > 0:\n
  id_list_list.append(id_list[-remaining_object_id_count:])\n
Folder_reindexObjectList(id_list_list=id_list_list)\n
\n
if tree_id_list is not None:\n
  if len(tree_id_list) > 0:\n
    # Calling again and again the same script allow to decrease the\n
    # number of activities by the same time and increase performance.\n
    folder.activate(activity=\'SQLQueue\', priority=object_priority,\n
      after_tag=tree_after_tag, \n
      tag=tree_tag).Folder_reindexTreeObjectList(\n
        tree_id=None,\n
        tree_id_list=tree_id_list,\n
        folder_tag=folder_tag,\n
        folder_after_tag=folder_after_tag,\n
        object_priority=object_priority,\n
        sql_catalog_id=sql_catalog_id,\n
        object_tag=object_tag,\n
        tree_after_tag=tree_after_tag,\n
        tree_tag=tree_tag,\n
        )\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>tree_id=None, tree_id_list=None, folder_tag=None, folder_after_tag=None, object_tag=None, object_after_tag=None, object_priority=1, sql_catalog_id=None, tree_tag=None, tree_after_tag=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Folder_reindexTreeObjectList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
