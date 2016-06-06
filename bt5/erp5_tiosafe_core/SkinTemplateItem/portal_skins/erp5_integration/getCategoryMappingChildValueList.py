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
            <value> <string>from Products.ERP5Type.Utils import sortValueList\n
\n
def getCategoryMappingChildValueList(category_mapping, sort_on=None, sort_order=None,\n
                  is_self_excluded=1,local_sort_method=None,\n
                  local_sort_id=None, **kw):\n
  if is_self_excluded:\n
    value_list = []\n
  else:\n
    value_list = [category_mapping]\n
  allowed_type_list = ["Integration Base Category Mapping","Integration Category Mapping"]\n
  child_value_list = category_mapping.objectValues(portal_type=allowed_type_list)\n
  if local_sort_id:\n
    if isinstance(local_sort_id, (tuple, list)):\n
      def sort_method(a, b):\n
        for sort_id in local_sort_id:\n
          diff = cmp(a.getProperty(sort_id, 0), b.getProperty(sort_id, 0))\n
          if diff != 0:\n
            return diff\n
        return 0\n
      local_sort_method = sort_method\n
    else:\n
      local_sort_method = lambda a, b: cmp(a.getProperty(local_sort_id, 0),\n
                                          b.getProperty(local_sort_id, 0))\n
  if local_sort_method:\n
    # sort objects at the current level\n
    child_value_list = list(child_value_list)\n
    child_value_list.sort(local_sort_method)\n
  # get recursive child value list\n
  for c in child_value_list:\n
    value_list.extend(getCategoryMappingChildValueList(c,\n
                                  is_self_excluded=0,\n
                                  local_sort_id=local_sort_id,\n
                                  local_sort_method=local_sort_method))\n
\n
  return sortValueList(value_list, sort_on, sort_order, **kw)\n
\n
\n
return getCategoryMappingChildValueList(context, sort_on=sort_on, sort_order=sort_order, \n
                                        local_sort_method=local_sort_method, \n
                                        local_sort_id=local_sort_id, **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>sort_on=None, sort_order=None, local_sort_method=None, local_sort_id=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>getCategoryMappingChildValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
