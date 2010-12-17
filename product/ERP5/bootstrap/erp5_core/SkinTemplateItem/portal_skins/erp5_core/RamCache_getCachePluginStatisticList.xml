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
            <value> <string>"""\n
This script will dynamically get cache statistics information and \n
format it so it can be used in a listbox field.\n
"""\n
from Products.ERP5Type.Document import newTempBase\n
\n
# get all cache statistics \n
cache_stats = context.getPortalObject().portal_caches.getCacheTotalMemorySize()\n
cache_factory_list_stats = cache_stats[\'stats\']\n
cache_plugin_id = context.getId()\n
cache_factory_id = context.getParentValue().getId()\n
cache_plugin_stats = cache_factory_list_stats[cache_factory_id]\n
cache_plugin_stats_data = cache_plugin_stats[\'cp_cache_keys_total_size\']\n
\n
if statistics_criteria == \'total\':\n
  # return just mrmotu usage for cache plugin\n
  return cache_plugin_stats[\'total\']\n
\n
result = []\n
counter = 0\n
for cache_key,cache_key_memory in cache_plugin_stats_data.items():\n
  obj = newTempBase(context, \n
                    \'temp_translation_%d\' %counter,\n
                    cache_key = cache_key,\n
                    cache_key_memory = cache_key_memory)\n
  obj.setUid(\'new_%d\' %counter)\n
  counter += 1\n
  result.append(obj)\n
\n
# sort result\n
if kw.get(\'sort_on\', None) is not None:\n
  sort_on_attr, sort_on_order = kw[\'sort_on\'][0]\n
  result.sort(key=lambda x: int(getattr(x, sort_on_attr)))\n
  if sort_on_order == \'descending\':\n
    result.reverse()\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>statistics_criteria=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>RamCache_getCachePluginStatisticList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
